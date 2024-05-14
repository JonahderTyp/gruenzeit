from flask import Blueprint, render_template, request, redirect, url_for, abort
from flask_login import current_user
from flask_login.utils import login_required, login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash
from ..database.db import user_type, user, TimeEntries, job, job_status
from ..database.exceptions import ElementAlreadyExists, ElementDoesNotExsist
from pprint import pprint
from datetime import datetime, timedelta
from typing import List

stempel_site = Blueprint("stempel", __name__, url_prefix="/stempel")


@stempel_site.route("/", methods=["GET", "POST"])
@login_required
def overview():
    usr: user = current_user
    baustellen_active = job.getJobs(job_status.query.get(1)) \
        + job.getJobs(job_status.query.get(2))

    userTimesToday: List[TimeEntries] = TimeEntries.getEntriesToday(usr)

    stempelung: List[dict] = []
    for entry in userTimesToday:
        if entry.start_time:
            duration: timedelta = (
                (entry.end_time if entry.end_time else datetime.now()) - entry.start_time)

        stempelung.append({
            "id": entry.id,
            "start_time": entry.start_time.strftime("%H:%M"),
            "end_time": entry.end_time.strftime("%H:%M") if entry.end_time else None,
            "duration": f"{str(duration).split('.')[0][:-3]}" if duration and duration.total_seconds() > 0 else None,
            # "timetype": {"name": entry.time_type.name, "id": entry.time_type.id},
            "job": entry.job.toDict() if entry.job else None,
        })

    # userstatus = TimeEntries.getUnfinishedEntries(usr)
    current_time = datetime.now()

    # pprint(timetypes)

    current_hour = current_time.hour
    current_minute = (current_time.minute // 15)*15

    return render_template("stempel/stempel.html",
                           userTimesToday=stempelung,
                           baustellen=baustellen_active,
                        #    timetypes=timetypes,
                           currHour=current_hour,
                           currMin=current_minute)


@stempel_site.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    usr: user = current_user
    if request.method == "POST":
        pass
    return render_template("stempel/edit.html")


@stempel_site.route("/start", methods=["POST"])
def start():
    usr: user = current_user
    if request.method == "POST":
        print(request.form)
        hours = request.form.get("hours")
        minutes = request.form.get("minutes")
        timetype_id = request.form.get("timetype")
        baustelle_id = request.form.get("baustelle")
        print(baustelle_id)
        if not hours or not minutes:
            return abort(401)
        try:
            hours = int(hours)
            minutes = int(minutes)
            entry_time = datetime.now().replace(
                hour=hours, minute=minutes, second=0, microsecond=0)
        except ValueError:
            return abort(400)
        try:
            TimeEntries.newEntry(usr, entry_time,
                                 job.getJob(baustelle_id) if baustelle_id else None)
        except ElementAlreadyExists as ex:
            print(ex)
            return abort(400)
        return redirect(url_for(".overview"))
