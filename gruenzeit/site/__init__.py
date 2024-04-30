from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import current_user
from flask_login.utils import login_required, login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash
from ..database.db import User

site = Blueprint("site", __name__, template_folder="templates", url_prefix="/")


@site.get("/")
def index():
    if not current_user.is_authenticated:
        print("user is not authenticated, redirecting to login...")
        return redirect(url_for('.login'))
    print("user is authenticated, redirecting to home...")
    return redirect(".home")


@site.route("/login", methods=["GET", "POST"])
def login():
    print("login", current_user)
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()
        # print("Username:", username)
        print("User:", user)
        # print("password:", password)
        # print("passwordHash:", user.password_hash)
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            print("login successful, user id:", user.username)  # Log user ID to verify
            return redirect(url_for('.home'))
        else:
            print("login failed")
            return render_template("login.html", error_message="Invalid username or password")
    if current_user.is_authenticated:
        print("user is already authenticated, redirecting to home...")
        return redirect(url_for('.home'))
    else:
        print("User is not Authenticated")
    return render_template("login.html")


@site.get("/logout")
def logout():
    logout_user()
    # Redirect to the index page after logout
    return redirect(url_for('site.index'))


@site.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        password = request.form["password"]

        # Check if the name already exists
        existing_user = User.query.filter_by(name=name).first()
        if existing_user:
            return render_template("register.html", error="Name already taken")

        # Create new user
        User.createNew(name, generate_password_hash(password))
        # Redirect to the login page after successful registration
        return redirect(url_for('site.login'))

    return render_template("register.html")


@site.route("/home")
@login_required
def home():
    print("rendering Home")
    return render_template("home.html")
