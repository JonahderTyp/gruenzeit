from flask import Blueprint, render_template, request, redirect, url_for, abort
from flask_login import current_user
from flask_login.utils import login_required
from ..database.db import user, job, job_status, Bild
from ..database.exceptions import ElementDoesNotExsist
from typing import List
import base64
from .forms import BaustelleForm

baustelle_site = Blueprint("baustelle", __name__, url_prefix="/baustelle")


@baustelle_site.before_request
@login_required
def auth():
    usr: user = current_user
    if not usr.user_type_id <= 3:
        abort(401)


@baustelle_site.route("/", methods=["GET", "POST"])
def overview():
    def jobToHtml(job: job):
        images = [i.bild for i in job.bilder]
        if len(images) == 0:
            with open("gruenzeit/static/baustelle.png", "rb") as image_file:
                # Convert the image to base64
                encoded_string = base64.b64encode(
                    image_file.read()).decode('utf-8')
            images = [encoded_string]

        return {
            "id": job.id,
            "nummer": job.auftragsnummer,
            "name": job.name,
            "adresse": job.adresse,
            "beschreibung": job.beschreibung[:50],
            "status": job_status.get(job.status_id).toDict(),
            "bilder": f"data:image/png;base64,{images[0]}"
        }

    error_message = ""
    if request.method == "POST":
        autragsnummer = request.form.get("auftragsnummer").strip()
        auftragsname = request.form.get("auftragsname").strip()
        auftragsadresse = request.form.get("auftragsadresse").strip()
        auftragsbeschreibung = request.form.get(
            "auftragsbeschreibung").strip().replace("\r\n", "\n")
        new_baustelle = job.createNew(autragsnummer, auftragsname,
                                      auftragsadresse, auftragsbeschreibung)
        return redirect(url_for(".baustelle", id=new_baustelle.id))

    bst1: List[dict] = [jobToHtml(i)
                        for i in job.getJobs(job_status.query.get(1))]
    bst2: List[dict] = [jobToHtml(i)
                        for i in job.getJobs(job_status.query.get(2))]

    return render_template("baustelle/overview.html",
                           baustellen1=bst1,
                           baustellen2=bst2)


@baustelle_site.route("/new", methods=["GET", "POST"])
def new():
    error_message = ""
    if request.method == "POST":
        autragsnummer = request.form.get("auftragsnummer").strip()
        auftragsname = request.form.get("auftragsname").strip()
        auftragsadresse = request.form.get("auftragsadresse").strip()
        auftragsbeschreibung = request.form.get(
            "auftragsbeschreibung").strip().replace("\r\n", "\n")

        new_baustelle = job.createNew(autragsnummer, auftragsname,
                                      auftragsadresse, auftragsbeschreibung)

        if 'file' in request.files:
            files = request.files.getlist('file')
            for file in files:
                if file:
                    content = base64.b64encode(
                        file.stream.read()).decode('utf-8')
                    Bild.uploadImage(new_baustelle, content)

        return redirect(url_for(".baustelle", id=new_baustelle.id))
    return render_template("baustelle/baustelle_new.html")


@baustelle_site.route("/<int:id>", methods=["GET"])
def baustelle(id):
    try:
        bst = job.getJob(id).toHTML()
    except ElementDoesNotExsist as ex:
        abort(404)
    return render_template("baustelle/baustelle.html", baustelle=bst)


@baustelle_site.route("/<int:id>/edit", methods=["GET", "POST"])
def edit(id):
    # if request.method == "POST":
    #     form = BaustelleForm(request.POST)

    error_message = ""
    statuses: List[job_status] = job_status.query.all()
    form: BaustelleForm = BaustelleForm()
    form.status.choices = [(status.id, status.name) for status in statuses]

    try:
        bst = job.getJob(id)
    except ElementDoesNotExsist as ex:
        error_message = repr(ex)
        abort(404)

    if form.is_submitted():
        print("Form submitted")
        if form.validate():
            print("Form validated")
            if form.submit_update.data:
                bst.auftragsnummer = form.auftragsnummer.data.strip()
                bst.name = form.auftragsname.data.strip()
                bst.adresse = form.auftragsadresse.data.strip()
                bst.beschreibung = form.auftragsbeschreibung.data.strip().replace("\r\n", "\n")
                bst.status_id = form.status.data
                bst.edit(bst.auftragsnummer, bst.name,
                         bst.adresse, bst.beschreibung)
                if 'file' in request.files:
                    files = request.files.getlist('file')
                    for file in files:
                        if file:
                            content = base64.b64encode(
                                file.stream.read()).decode('utf-8')
                            Bild.uploadImage(bst, content)
                return redirect(url_for(".baustelle", id=id))
            elif form.submit_delete.data:
                job.deleteJob(id)
                return redirect(url_for(".baustellen"))
        else:
            print(form.errors)

    # Pre-fill the form with existing job data
    form.auftragsnummer.data = bst.auftragsnummer
    form.auftragsname.data = bst.name
    form.auftragsadresse.data = bst.adresse
    form.auftragsbeschreibung.data = bst.beschreibung
    form.status.data = bst.status_id

    return render_template("baustelle/baustelleedit.html", form=form, baustelle=bst.toHTML(), statuses=statuses, error_message=error_message)


@baustelle_site.route("/encode", methods=["GET", "POST"])
def encode():
    error_message = ""
    if request.method == "POST":
        autragsnummer = request.form.get("auftragsnummer").strip()
        auftragsname = request.form.get("auftragsname").strip()
        auftragsadresse = request.form.get("auftragsadresse").strip()
        auftragsbeschreibung = request.form.get(
            "auftragsbeschreibung").strip().replace("\r\n", "\n")

        if 'file' in request.files:
            files = request.files.getlist('file')
            for file in files:
                if file:
                    content = base64.b64encode(
                        file.stream.read()).decode('utf-8')
                    return content

        abort(400)
    return render_template("baustelle/baustelle_new.html")
