from flask import Blueprint, render_template, request, redirect, url_for, abort
from flask_login import current_user
from flask_login.utils import login_required
from werkzeug.security import generate_password_hash
from ..database.db import user_type, user
from ..database.exceptions import ElementAlreadyExists

admin_site = Blueprint("admin", __name__, url_prefix="/admin")


@admin_site.before_request
@login_required
def auth():
    usr: user = current_user
    if not usr.user_type_id == 1:
        abort(401)


@admin_site.get("/")
def admin():
    return render_template("admin/admin.html")


@admin_site.route("/adduser", methods=["GET", "POST"])
def addUser():
    error_message = None
    types = user_type.query.all()
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        name = request.form.get("name", "").strip()
        password = request.form.get("password", "").strip()
        usertype = request.form.get("usertype", "")
        if username and name and password and usertype:
            try:
                newUser = user.createNew(
                    username, name, generate_password_hash(password), usertype)
                print("NEW USER", newUser.toDict())
                print("Username:", newUser.username)
                return redirect(url_for(".getuser", username=newUser.username))
            except ElementAlreadyExists as ex:
                error_message = repr(ex)
        else:
            error_message = "Fehler in der Eingabe, mindestens ein Wert Fehlt"
    return render_template("admin/newUser.html", types=types, error_message=error_message)


@admin_site.get("/users")
def users():
    usertypes = user_type.query.all()
    print(usertypes)
    users = [i.__dict__ for i in user.query.all()]
    for usr in users:
        usr["user_type"] = user_type.query.get(usr['user_type_id']).name
    return render_template("admin/users.html", user=users)


@admin_site.get("/users/<username>")
def getuser(username):
    usr: user = user.query.get(username)
    return render_template("admin/user.html", user=usr)
