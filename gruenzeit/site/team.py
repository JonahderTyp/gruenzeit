from flask import Blueprint, render_template, redirect, url_for, abort
from flask_login import current_user
from flask_login.utils import login_required
from ..database.db import user, vehicle
from .forms import VehicleSelectForm

team_site = Blueprint("team", __name__, url_prefix="/team")


@team_site.before_request
@login_required
def auth():
    usr: user = current_user
    if not usr.user_type_id <= 3:
        abort(401)


@team_site.route("/", methods=["GET", "POST"])
def overview():
    usr: user = current_user
    form = VehicleSelectForm()
    form.vehicle.choices.extend([(v.id, f"{v.name}  [{v.kennzeichen}]")
                                for v in vehicle.getVehicles()])

    if form.validate_on_submit():
        selected_vehicle_id = form.vehicle.data
        if int(selected_vehicle_id) == -1:
            usr.setVehicle(None)
        else:
            selected_vehicle = vehicle.getVehicle(selected_vehicle_id)
            usr.setVehicle(selected_vehicle)
        return redirect(url_for('.overview'))

    current_vehicle = usr.getVehicle()
    team_members = usr.getTeamMembers() if current_vehicle else []

    return render_template("team/overview.html", form=form, current_vehicle=current_vehicle, team_members=team_members)
