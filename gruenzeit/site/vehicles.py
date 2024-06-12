from flask import Blueprint, render_template, redirect, url_for, abort
from flask_login import current_user
from flask_login.utils import login_required
from ..database.db import user, vehicle
from .forms import VehicleForm

vehicle_site = Blueprint("vehicle", __name__, url_prefix="/fahrzeug")


@vehicle_site.before_request
@login_required
def auth():
    usr: user = current_user
    if not usr.user_type_id <= 2:
        abort(401)


@vehicle_site.route("/", methods=["GET", "POST"])
def overview():
    vehicles = vehicle.getVehicles()
    return render_template("vehicle/overview.html", vehicles=vehicles)


@vehicle_site.route("/new", methods=["GET", "POST"])
def new():
    form = VehicleForm()
    if form.validate_on_submit():
        name = form.name.data
        kennzeichen = form.kennzeichen.data
        vehicle.newVehicle(name, kennzeichen)
        return redirect(url_for(".overview"))
    return render_template("vehicle/new.html", form=form)


@vehicle_site.route("/<int:id>/edit", methods=["GET", "POST"])
def edit(id):
    vec = vehicle.getVehicle(id)
    form = VehicleForm(obj=vec)
    if form.validate_on_submit():
        vec.update(name=form.name.data, kennzeichen=form.kennzeichen.data)
        return redirect(url_for(".overview"))
    return render_template("vehicle/edit.html", form=form, vehicle=vec)
