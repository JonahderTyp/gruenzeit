from flask import Blueprint, render_template, request, redirect, url_for, abort
from flask_login import current_user
from flask_login.utils import login_required, login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash
from ..database.db import user_type, user, TimeEntries, TimeType, job, job_status
from ..database.exceptions import ElementAlreadyExists, ElementDoesNotExsist
from pprint import pprint
from datetime import datetime

stempel_site = Blueprint("stempel", __name__, url_prefix="/stempel")


@stempel_site.route("/", methods=["GET", "POST"])
@login_required
def overview():
    usr: user = current_user
    baustellen_active = job.getJobs(job_status.query.get(1))
    timetypes = TimeType.getList()
    userstatus = TimeEntries.getUnfinishedEntries(usr)
    current_time = datetime.now()

    pprint(timetypes)

    current_hour = current_time.hour
    current_minute = (current_time.minute // 15)*15

    return render_template("stempel/stempel.html",
                           userstatus=userstatus,
                           baustellen=baustellen_active,
                           timetypes=timetypes,
                           currHour=current_hour,
                           currMin=current_minute)


@stempel_site.route("/start", methods=["POST"])
def start():
    usr: user = current_user
    if request.method == "POST":
        print(request.form)
        hours = request.form.get("hours")
        minutes = request.form.get("minutes")
        timetype_id = request.form.get("timetype")
        baustelle_id = request.form.get("baustelle")
        timetype = TimeType.query.get(timetype_id)
        if not hours or not minutes or not timetype:
            return abort(401)
        try:
            hours = int(hours)
            minutes = int(minutes)
            entry_time = datetime.now().replace(
                hour=hours, minute=minutes, second=0, microsecond=0)
        except ValueError:
            return abort(400)
        try:
            TimeEntries.newEntry(usr, timetype, entry_time, job.getJob(baustelle_id))
        except ElementAlreadyExists as ex:
            print(ex)
            return abort(400)
        return redirect(url_for(".overview"))
