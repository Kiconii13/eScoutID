from datetime import datetime

from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user

from models import User, db
from models.activity import Activity, Participation,OrganizerLevel


aktivnosti_bp = Blueprint('aktivnosti', __name__)


@aktivnosti_bp.route("/aktivnosti")
@login_required
def aktivnosti():
    activities = Activity.query.all()

    return render_template("aktivnosti.html", activities=activities)


@aktivnosti_bp.route("/addAktivnost")
@login_required
def addAktivnost():
    if current_user.role == "admin":
        activities = Activity.query.filter_by(organizer_name = current_user.odred.name).all()
    elif current_user.role == "savez_admin":
        activities = Activity.query.filter(Activity.organizer_type != OrganizerLevel(1))

    filtered_users = User.query.all()

    return render_template("addAktivnost.html", user_list=filtered_users, activities=activities)


@aktivnosti_bp.route("/aktivnosti/new", methods=["POST"])
@login_required
def new_aktivnost():
    aktivnost = Activity()
    aktivnost.name = request.form["name"]
    aktivnost.due_date = datetime.fromisoformat(request.form["due_date"]).date()
    aktivnost.location = request.form["location"]
    aktivnost.type = request.form["type"]
    if current_user.role == "savez_admin":
        aktivnost.organizer_type = request.form["organizer_type"]
        aktivnost.organizer_name = request.form["organizer_name"]
    elif current_user.role == "admin":
        aktivnost.organizer_type = OrganizerLevel(1)
        aktivnost.organizer_name = current_user.odred.name
    db.session.add(aktivnost)
    db.session.commit()

    flash("Aktivnost uspešno kreirana", "Info")
    return redirect(url_for("aktivnosti.addAktivnost"))


@aktivnosti_bp.route("/aktivnosti/log", methods=["POST"])
@login_required
def log_aktivnost():
    participation = Participation()

    participation.activity_id = request.form["activity"]
    participation.user_id = request.form["user"]

    db.session.add(participation)
    db.session.commit()

    flash("Učešće uspešno zabeleženo", "Info")
    return redirect(url_for("aktivnosti.addAktivnost"))
