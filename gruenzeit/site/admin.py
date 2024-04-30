from flask import Blueprint, render_template, request, redirect, url_for, abort
from flask_login import current_user
from flask_login.utils import login_required, login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash
from ..database.db import UserType, User

admin_site = Blueprint("admin", __name__, url_prefix="/admin")

@admin_site.before_request
@login_required
def auth():
    usr: User = current_user
    if not usr.usertype_id == 1:
        abort(401)


@admin_site.route("/")
def admin():
    return render_template("admin/admin.html")


@admin_site.route("/adduser")
def addUser():
    types = UserType.query.all()
    return render_template("admin/newUser.html", types=types)

@admin_site.route("/users")
def users():
    user = User.query.all()
    return render_template("admin/users.html", user=user)