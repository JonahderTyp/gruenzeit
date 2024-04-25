from flask import Blueprint, render_template

site = Blueprint("site", __name__, template_folder="templates")

@site.get("/")
def index():
    return render_template("index.html")