from flask import Blueprint, render_template, request, redirect, url_for, abort, send_file
from flask_login.utils import login_required
from .pdf.pdf import pdfGen

exports_site = Blueprint("exports", __name__, url_prefix="/exports")

# reqire the user to be logged in
@exports_site.before_request
@login_required
def before_request():
    pass

@exports_site.route("/", methods=["GET", "POST"])
def overview():
    return render_template("exports/overview.html")

@exports_site.route("/mitarbeiter", methods=["GET", "POST"])
def export():
    date = request.args.get("date")
    p = pdfGen()

    pdf_buffer = p.generate()
    print("EXPORT")
    print(date)
    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name=f'mitarbeiter-{date}.pdf',
        mimetype='application/pdf'
    )

