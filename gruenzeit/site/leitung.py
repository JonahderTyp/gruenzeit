from flask import Blueprint, render_template, request, redirect, url_for, abort
from flask_login import current_user
from flask_login.utils import login_required, login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash
from ..database.db import UserType, User, TimeEntries, Baustelle, BaustellenStatus
from ..database.exceptions import ElementAlreadyExists, ElementDoesNotExsist
from pprint import pprint
from typing import List

leitung_site = Blueprint("leitung", __name__, url_prefix="/leitung")


@leitung_site.before_request
@login_required
def auth():
    usr: User = current_user
    if not usr.usertype_id <= 2:
        abort(401)


@leitung_site.route("/baustelle", methods=["GET", "POST"])
def baustellen():
    error_message = ""
    if request.method == "POST":
        autragsnummer = request.form.get("auftragsnummer").strip()
        auftragsname = request.form.get("auftragsname").strip()
        auftragsadresse = request.form.get("auftragsadresse").strip()
        auftragsbeschreibung = request.form.get(
            "auftragsbeschreibung").strip().replace("\r\n", "\n")
        new_baustelle = Baustelle.createNew(autragsnummer, auftragsname,
                                            auftragsadresse, auftragsbeschreibung)
        return redirect(url_for(".baustelle", id=new_baustelle.id))
    bst: List[Baustelle] = Baustelle.query.all()
    return render_template("leitung/baustellen.html", baustellen=bst)


@leitung_site.route("/baustelle/<int:id>", methods=["GET"])
def baustelle(id):
    bst = Baustelle.getBaustelleHTML(id)
    return render_template("leitung/baustelle.html", baustelle=bst)


@leitung_site.route("/baustelle/<int:id>/edit", methods=["GET", "POST"])
def edit(id):
    error_message = ""
    statuses = BaustellenStatus.query.all()
    try:
        bst = Baustelle.getBaustelleHTML(id)
    except ElementDoesNotExsist as ex:
        error_message = repr(ex)
        abort(404)
    if request.method == "POST":
        if "edit" in request.form:
            auftragsnummer = request.form.get("auftragsnummer").strip()
            auftragsname = request.form.get("auftragsname").strip()
            auftragsadresse = request.form.get("auftragsadresse").strip()
            auftragsbeschreibung = request.form.get(
                "auftragsbeschreibung").strip().replace("\r\n", "\n")
            bst.edit(auftragsnummer, auftragsname,
                     auftragsadresse, auftragsbeschreibung)
            return redirect(url_for(".baustelle", id=id))
        elif "delete" in request.form:
            bst = Baustelle.query.get(id)
            bst.delete()
            return redirect(url_for(".baustellen"))
        elif "status" in request.form:
            status = request.form.get("status")
            bst = Baustelle.query.get(id)
            bst.status = status
            bst.save()
            return redirect(url_for(".baustelle", id=id))
    return render_template("leitung/baustelleedit.html", baustelle=bst, statuses=statuses, error_message=error_message)
