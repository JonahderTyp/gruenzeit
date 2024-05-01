from flask import Blueprint, render_template, request, redirect, url_for, abort
from flask_login import current_user
from flask_login.utils import login_required, login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash
from ..database.db import UserType, User
from ..database.exceptions import ElementAlreadyExists, ElementDoesNotExsist
from pprint import pprint

admin_site = Blueprint("admin", __name__, url_prefix="/admin")


@admin_site.before_request
@login_required
def auth():
    usr: User = current_user
    if not usr.usertype_id == 1:
        abort(401)


@admin_site.get("/")
def admin():
    return render_template("admin/admin.html")


@admin_site.route("/adduser", methods=["GET", "POST"])
def addUser():
    error_message = None
    types = UserType.query.all()
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        name = request.form.get("name", "").strip()
        password = request.form.get("password", "").strip()
        usertype = request.form.get("usertype", "")
        if username and name and password and usertype:
            try:
                newUser = User.createNew(
                    username, name, generate_password_hash(password), usertype)
                return redirect(url_for(".user", username=newUser.username))
            except ElementAlreadyExists as ex:
                error_message = repr(ex)
        else:
            error_message = "Fehler in der Eingabe, mindestens ein Wert Fehlt"
    return render_template("admin/newUser.html", types=types, error_message=error_message)


@admin_site.get("/users")
def users():
    usertypes = UserType.query.all()
    print(usertypes)
    user = [i.__dict__ for i in User.query.all()]
    for usr in user:
        usr["usertype"] = UserType.query.get(usr['usertype_id']).name

    pprint(user)
    return render_template("admin/users.html", user=user)


@admin_site.get("/users/<username>")
def user(username):
    user: User = User.query.get(username)
    return render_template("admin/user.html", user=user)
