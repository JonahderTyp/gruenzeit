from flask import Blueprint, render_template

site = Blueprint("site", __name__, template_folder="templates", url_prefix="/")

@site.get("/")
def index():
    return render_template("index.html")