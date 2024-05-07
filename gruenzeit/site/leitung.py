from flask import Blueprint, render_template, request, redirect, url_for, abort
from flask_login import current_user
from flask_login.utils import login_required, login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash
from ..database.db import UserType, User, TimeEntries, Baustelle
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
    id = request.values.get("id", None)
    if request.method == "POST":
        autragsnummer = request.form.get("auftragsnummer").strip()
        auftragsname = request.form.get("auftragsname").strip()
        auftragsadresse = request.form.get("auftragsadresse").strip()
        auftragsbeschreibung = request.form.get(
            "auftragsbeschreibung").strip().replace("\r\n", "\n")
        new_baustelle = Baustelle.createNew(autragsnummer, auftragsname,
                                            auftragsadresse, auftragsbeschreibung)
        return redirect(url_for(".baustellen", id=new_baustelle.id))
    if id:
        # TODO edit baustelle
        # TODO delete baustelle
        # TODO set baustelle status
        bst : Baustelle | None = Baustelle.query.get({"id": id})
        bst.beschreibung = str(bst.beschreibung).split("\n")
        return render_template("leitung/baustelle.html", baustelle=bst)
    
    bst: List[Baustelle] = Baustelle.query.all()
    return render_template("leitung/baustellen.html", baustellen=bst)
