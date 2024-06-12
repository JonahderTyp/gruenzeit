from flask import Blueprint, render_template, request
from flask_login.utils import login_required
from ..database.db import TimeEntries
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


@exports_site.get("/print")
def userprint():
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

    return render_template("exports/print.html", date=str(reqdate.date()) , entries=stempelung)
