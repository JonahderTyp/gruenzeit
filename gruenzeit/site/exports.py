from flask import Blueprint, render_template, request, abort
from flask_login.utils import login_required
from ..database.db import TimeEntries, job, user
from datetime import datetime, date, timedelta
from typing import List

exports_site = Blueprint("exports", __name__, url_prefix="/exports")

# reqire the user to be logged in
@exports_site.before_request
@login_required
def before_request():
    pass


@exports_site.route("/", methods=["GET", "POST"])
def overview():
    return render_template("exports/overview.html")


@exports_site.get("/daily")
def dailyexport():
    reqdateraw = request.args.get("date", date.today().isoformat())
    reqdate = datetime.fromisoformat(reqdateraw)

    entries = TimeEntries.getEntriesOfDate(reqdate)
    entries.sort(key=lambda x: x.user_id)

    stempelung: List[dict] = []
    for entry in entries:
        
        duration: timedelta = (
            (entry.end_time if entry.end_time else datetime.now()) - entry.start_time)
        
        work_time = duration - timedelta(minutes=entry.pause_time)

        stempelung.append({
            "id": entry.id,
            "start_time": {"str": entry.start_time.strftime("%H:%M"),
                           "hour": entry.start_time.strftime("%H"),
                           "minute": entry.start_time.strftime("%M")},
            "end_time": {"str": entry.end_time.strftime("%H:%M"),
                         "hour": entry.end_time.strftime("%H"),
                         "minute": entry.end_time.strftime("%M")} if entry.end_time else None,
            "pause_time": {"str": (f"{entry.pause_time // 60}h " if entry.pause_time > 59 else "") + f"{entry.pause_time % 60}min",
                           "hour": entry.pause_time // 60,
                           "minute": entry.pause_time % 60},
            "work_time": {
                "str": work_time.__str__().split('.')[0][:-3],
                "hour": work_time.seconds // 3600,
                "minute": (work_time.seconds % 3600) // 60
            },

            "duration": f"{str(duration).split('.')[0][:-3]}" if duration and duration.total_seconds() > 0 else None,
            # "timetype": {"name": entry.time_type.name, "id": entry.time_type.id},
            "job": entry.job.toDict() if entry.job else None,
            "user": {
                "name": entry.user.name,
                "id": entry.user.username}
        })

    return render_template("exports/daily.html", date=str(reqdate.date()) , entries=stempelung)



@exports_site.get("/jobexport")
def jobexport():
    jobid = request.args.get("jobid")
    if not jobid:
        return abort(400, "No job ID provided")
    
    baustelle = job.getJob(jobid)
    
    timestamps = baustelle.getTimestamps()

    # sort timestamps by job
    timestamps.sort(key=lambda x: x.job_id)
    timestamps.sort(key=lambda x: x.user_id)

    accumilatedTimes = {}

    for timestamp in timestamps:
        if not timestamp.user.name in accumilatedTimes.keys():
            accumilatedTimes[timestamp.user.get_id()] = timestamp.getWorkTime().seconds/60
        else:
            accumilatedTimes[timestamp.user.get_id()] += timestamp.getWorkTime().seconds/60

        

    usertimes : List[dict] = []

    for time in accumilatedTimes:
        usr = user.getUser(time)
        usertimes.append({
            "user": {
                "name": usr.name,
                "id": usr.username},
            "work_time": {
                "str": str(timedelta(minutes=accumilatedTimes[time])).split('.')[0][:-3],
                "hour": accumilatedTimes[time] // 60,
                "minute": accumilatedTimes[time] % 60
            },
        })

    return render_template("exports/job.html", usertimes=usertimes, baustelle=baustelle.toHTML(), date=str(date.today()))