from flask import Blueprint, render_template, request, redirect, url_for, abort
from flask_login import current_user
from flask_login.utils import login_required, login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash
from ..database.db import user_type, user, TimeEntries, job, job_status, Bild
from ..database.exceptions import ElementAlreadyExists, ElementDoesNotExsist
from pprint import pprint
from typing import List
import base64

baustelle_site = Blueprint("baustelle", __name__, url_prefix="/baustelle")


@baustelle_site.before_request
@login_required
def auth():
    usr: user = current_user
    if not usr.user_type_id <= 2:
        abort(401)


@baustelle_site.route("/", methods=["GET", "POST"])
def overview():
    with open("gruenzeit/static/baustelle.png", "rb") as image_file:
        # Convert the image to base64
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')

    def jobToHtml(job: job):
        images = job.bilder
        if len(images) == 0:
            images = [f"data:image/png;base64,{encoded_string}"]

        return {
            "id": job.id,
            "nummer": job.auftragsnummer,
            "name": job.name,
            "adresse": job.adresse,
            "beschreibung": job.beschreibung[:50],
            "status": job_status.get(job.status_id).toDict(),
            "bilder": images
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

    # pprint(bst1)

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
        pprint([i[:10] for i in bst.get("bilder")])
    except ElementDoesNotExsist as ex:
        abort(404)
    return render_template("baustelle/baustelle.html", baustelle=bst)


@baustelle_site.route("/<int:id>/edit", methods=["GET", "POST"])
def edit(id):
    error_message = ""
    statuses = job_status.query.all()
    try:
        bst = job.getJob(id)
    except ElementDoesNotExsist as ex:
        error_message = repr(ex)
        abort(404)

    if request.method == "POST":
        pprint(request.form)
        if "auftragsnummer" in request.form:
            print("auftragsnummer gegeben")
            bst.auftragsnummer = request.form.get("auftragsnummer").strip()

        if "auftragsname" in request.form:
            print("auftragsname gegeben")
            bst.name = request.form.get("auftragsname").strip()

        if "auftragsadresse" in request.form:
            print("auftragsadresse gegeben")
            bst.adresse = request.form.get("auftragsadresse").strip()

        if "auftragsbeschreibung" in request.form:
            print("auftragsbeschreibung gegeben")
            bst.beschreibung = request.form.get(
                "auftragsbeschreibung").strip().replace("\r\n", "\n")

        if "status" in request.form:
            print("status gegeben")

            try:
                status = int(request.form.get("status"))
                job_status.get(status)
            except Exception as ex:
                abort(400)
                error_message = "Status existiert nicht"
                return render_template("baustelle/baustelleedit.html", baustelle=bst, statuses=statuses, error_message=error_message)
            bst.status_id = status

        return redirect(url_for(".baustelle", id=id))

    return render_template("baustelle/baustelleedit.html", baustelle=bst.toHTML(), statuses=statuses, error_message=error_message)


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
    