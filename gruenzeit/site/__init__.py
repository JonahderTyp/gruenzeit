from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import current_user
from flask_login.utils import login_required, login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash
from ..database.db import user
from .admin import admin_site
from .stempel import stempel_site
from .baustelle import baustelle_site
from .exports import exports_site
from .vehicles import vehicle_site
from .team import team_site
from .forms import ChangePasswordForm

site = Blueprint("site", __name__, template_folder="templates", url_prefix="/")

site.register_blueprint(admin_site)
site.register_blueprint(stempel_site)
site.register_blueprint(baustelle_site)
site.register_blueprint(exports_site)
site.register_blueprint(vehicle_site)
site.register_blueprint(team_site)


@site.context_processor
def inject_views():
    if not current_user.is_authenticated:
        return {"views": []}
    usr: user = current_user
    views = []

    # Mitarbeiter, Geschäftsführung und Admin
    if usr.user_type_id <= 3:
        views.append({"name": "Stempeln",
                      "url": url_for("site.stempel.overview"),
                      "description": "Erfasse Deine Arbeitszeiten"})
        views.append({"name": "Baustellen",
                      "url": url_for("site.baustelle.overview"),
                      "description": "Verwalte Baustellen"})
        views.append({"name": "Team",
                      "url": url_for("site.team.overview"),
                      "description": "Verwalte Dein Team"})

    # Geschäftsführung und Admin
    if usr.user_type_id <= 2:
        views.append({"name": "Export",
                      "url": url_for("site.exports.overview"),
                      "description": "Zeiterfassung exportieren"})
        views.append({"name": "Fahrzeuge",
                      "url": url_for("site.vehicle.overview"),
                      "description": "Fahrzeuge verwalten"})

    # Admin
    if usr.user_type_id == 1:
        views.append({"name": "Einstellungen",
                      "multi": [{"name": "admin",
                                 "url": url_for("site.admin.admin"),
                                 "description": "Admin Einstellungen"},
                                {"name": "Benutzer",
                                 "url": url_for("site.admin.users"),
                                 "description": "Benutzer verwalten"},
                                {"name": "Neuer Benutzer",
                                 "url": url_for("site.admin.addUser"),
                                 "description": "Neuen Benutzer anlegen"},
                                ],
                      "description": "Einstellungen"})
    views.append({"name": "Profil",
                  "multi": [{"name": "Passwort ändern",
                             "url": url_for("site.changePassword"),
                             "description": "Passwort ändern"},
                            {"name": "Logout",
                             "url": url_for("site.logout"),
                             "description": "Abmelden"}]
                  })
    # views.append({"name": "Logout",
    #               "url": url_for("site.logout")})
    return {"views": views}


@site.get("/")
def index():
    if not current_user.is_authenticated:
        print("user is not authenticated, redirecting to login...")
        return redirect(url_for('.login'))
    print("user is authenticated, redirecting to home...")
    return redirect(url_for(".home"))


@site.get("/favicon.ico")
def favicon():
    return redirect(url_for('static', filename='favicon.ico'))


@site.route("/login", methods=["GET", "POST"])
def login():
    print("login", current_user)
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"].strip()
        usr: user = user.query.filter_by(username=username).first()
        # print("Username:", username)
        print("User:", usr)
        # print("password:", password)
        # print("passwordHash:", user.password_hash)
        if usr and check_password_hash(usr.password_hash, password):
            login_user(usr, remember=True)
            # Log user ID to verify
            print("login successful, user id:", usr.username)
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


@site.route("/changePassword", methods=["GET", "POST"])
@login_required
def changePassword():
    usr: user = current_user
    form = ChangePasswordForm()
    if form.validate_on_submit():
        print("setting new password")
        usr.setNewPassword(generate_password_hash(form.new_password.data))
        logout_user()
        return redirect(url_for('site.index'))
    else:
        print("something is invalid")
    print(form.errors)
    return render_template("changePassword.html", form=form)


@site.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        password = request.form["password"]

        # Check if the name already exists
        existing_user = user.query.filter_by(name=name).first()
        if existing_user:
            return render_template("register.html", error="Name already taken")

        # Create new user
        user.createNew(name, generate_password_hash(password))
        # Redirect to the login page after successful registration
        return redirect(url_for('site.login'))

    return render_template("register.html")


@site.route("/home")
@login_required
def home():
    print("rendering Home")
    return render_template("home.html")
