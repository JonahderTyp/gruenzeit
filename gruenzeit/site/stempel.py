from flask import Blueprint, render_template, request, redirect, url_for, abort
from flask_login import current_user
from flask_login.utils import login_required
from ..database.db import user, TimeEntries, job, job_status
from ..database.exceptions import ElementAlreadyExists, ElementDoesNotExsist
from datetime import datetime, timedelta
from typing import List

stempel_site = Blueprint("stempel", __name__, url_prefix="/stempel")

# reqire the user to be logged in


@stempel_site.before_request
@login_required
def before_request():
    pass


@stempel_site.route("/", methods=["GET", "POST"])
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
            "start_time": {"str": entry.start_time.strftime("%H:%M"),
                           "hour": entry.start_time.strftime("%H"),
                           "minute": entry.start_time.strftime("%M")},
            "end_time": {"str": entry.end_time.strftime("%H:%M"),
                         "hour": entry.end_time.strftime("%H"),
                         "minute": entry.end_time.strftime("%M")} if entry.end_time else None,
            "pause_time": {"str": f"{entry.pause_time // 60}h {entry.pause_time % 60}m",
                           "hour": entry.pause_time // 60,
                           "minute": entry.pause_time % 60},

            "duration": f"{str(duration).split('.')[0][:-3]}" if duration and duration.total_seconds() > 0 else None,
            # "timetype": {"name": entry.time_type.name, "id": entry.time_type.id},
            "job": entry.job.toDict() if entry.job else None,
        })

    current_time = datetime.now()
    current_hour = ("0" + str(current_time.hour))[-2:]
    current_minute = ("0" + str((current_time.minute // 15)*15))[-2:]

    return render_template("stempel/overview.html",
                           userTimesToday=stempelung,
                           baustellen=baustellen_active,
                           #    timetypes=timetypes,
                           currHour=current_hour,
                           currMin=current_minute)


@stempel_site.route("/new", methods=["GET", "POST"])
def new():
    usr: user = current_user
    baustellen_active = job.getJobs(job_status.query.get(1)) \
        + job.getJobs(job_status.query.get(2))

    current_time = datetime.now()
    current_hour = ("0" + str(current_time.hour))[-2:]
    current_minute = ("0" + str((current_time.minute // 15)*15))[-2:]

    return render_template("stempel/new.html",
                           baustellen=baustellen_active,
                           currHour=current_hour,
                           currMin=current_minute)


@stempel_site.post("/edit/<int:id>")
def edit(id):
    usr: user = current_user
    if not request.method == "POST":
        return abort(400)

    try:
        entry = TimeEntries.getEntry(id)
    except ElementDoesNotExsist:
        return abort(404)

    if entry.user != usr:
        return abort(403)

    starthours = request.form.get("starthours")
    startminutes = request.form.get("startminutes")
    endhours = request.form.get("endhours")
    endminutes = request.form.get("endminutes")
    pausehours = request.form.get("pausehours")
    pauseminutes = request.form.get("pauseminutes")
    baustelle_id = request.form.get("baustelle")
    is_team_entry = request.form.get("teamCheck") is not None

    if not starthours or not startminutes or not endhours or not endminutes:
        return abort(400)

    try:
        starthours = int(starthours)
        startminutes = int(startminutes)
        start_time = datetime.now().replace(
            hour=starthours, minute=startminutes, second=0, microsecond=0)

        endhours = int(endhours)
        endminutes = int(endminutes)
        end_time = datetime.now().replace(
            hour=endhours, minute=endminutes, second=0, microsecond=0)

        pausehours = int(pausehours)
        pauseminutes = int(pauseminutes)
        pause_time = pausehours*60 + pauseminutes
    except ValueError:
        return abort(400)

    try:
        entry.edit(start_time, end_time, pause_time,
                   job.getJob(baustelle_id) if baustelle_id else None, is_team_entry)
    except ValueError as ex:
        print(ex)
        return abort(400)

    return redirect(url_for(".overview"))


@stempel_site.route("/start", methods=["POST"])
def start():
    usr: user = current_user
    if request.method == "POST":
        starthours = request.form.get("starthours")
        startminutes = request.form.get("startminutes")
        endhours = request.form.get("endhours")
        endminutes = request.form.get("endminutes")
        pausehours = request.form.get("pausehours")
        pauseminutes = request.form.get("pauseminutes")
        baustelle_id = request.form.get("baustelle")
        is_team_entry = request.form.get("teamCheck") is not None

        if not starthours or not startminutes or not endhours or not endminutes:
            return abort(400)
        try:
            starthours = int(starthours)
            startminutes = int(startminutes)
            start_time = datetime.now().replace(
                hour=starthours, minute=startminutes, second=0, microsecond=0)

            endhours = int(endhours)
            endminutes = int(endminutes)
            end_time = datetime.now().replace(
                hour=endhours, minute=endminutes, second=0, microsecond=0)

            pausehours = int(pausehours)
            pauseminutes = int(pauseminutes)
            pause_time = pausehours*60 + pauseminutes
        except ValueError:
            return abort(400)
        try:
            TimeEntries.newEntry(usr, start_time, end_time, pause_time,
                                 job.getJob(baustelle_id) if baustelle_id else None, is_team_entry)
        except ElementAlreadyExists as ex:
            print(ex)
            return abort(400)
        return redirect(url_for(".overview"))
