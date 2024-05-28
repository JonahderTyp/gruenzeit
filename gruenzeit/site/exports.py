from flask import Blueprint, render_template, request, redirect, url_for, abort
from flask_login.utils import login_required

exports_site = Blueprint("exports", __name__, url_prefix="/exports")

# reqire the user to be logged in
@exports_site.before_request
@login_required
def before_request():
    pass

@exports_site.route("/", methods=["GET", "POST"])
def overview():
    return render_template("exports/overview.html")

