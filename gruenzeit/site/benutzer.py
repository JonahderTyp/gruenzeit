from flask import Blueprint, render_template, request, redirect, url_for, abort
from flask_login import current_user
from flask_login.utils import login_required, login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash
from ..database.db import UserType, User, TimeEntries
from ..database.exceptions import ElementAlreadyExists, ElementDoesNotExsist
from pprint import pprint

benutzer_site = Blueprint("benutzer", __name__, url_prefix="/benutzer")


@benutzer_site.get("/")
@login_required
def index():
    usr: User = current_user
    userstatus = TimeEntries.getCurrentEntry(usr)
    useravailable = TimeEntries.getAvailableEntrys(usr)
    return render_template("mitarbeiter/stempel.html", userstatus=userstatus, useravailable=useravailable)

@benutzer_site.get("/stempeln")
@login_required
def stempeln():
    return redirect(url_for(".index"))
    return render_template()