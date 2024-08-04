from datetime import datetime

from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user

from models import User, db
from models.activity import Activity, Participation, OrganizerLevel

import qrcode
from io import BytesIO
from base64 import b64encode

aktivnosti_bp = Blueprint('aktivnosti', __name__)

# Prikaz svih aktivnosti u kojima je ucestvovao ulogovani clan
@aktivnosti_bp.route("/aktivnosti")
@login_required
def aktivnosti():
    activities = Activity.query.all()

    return render_template("aktivnosti.html", activities=activities)


# Prikaz stranice za dodavanje i dodeljivanje aktivnosti
@aktivnosti_bp.route("/addAktivnost")
@login_required
def addAktivnost():
    if current_user.role == "admin":
        # admin odreda dodaje samo aktivnosti koje organizuje njegov odred
        activities = Activity.query.filter_by(organizer_name=current_user.odred.name).all()
    elif current_user.role == "savez_admin":
        # savez_admin dodaje aktivnosti koje organizuje savez ili neka od internacionalnih organinzacija
        activities = Activity.query.filter(Activity.organizer_type != OrganizerLevel(1))
    else:
        # Mogu da pristupe samo admini
        return redirect(url_for("dashboard.dashboard"))

    return render_template("addAktivnost.html", activities=activities)


# Dodavanje nove aktivnosti u bazu
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


# Dodeljivanje aktivnosti clanovima
@aktivnosti_bp.route("/aktivnosti/log", methods=["POST"])
@login_required
def log_aktivnost():
    participation = Participation()

    participation.activity_id = request.form["activity"]
    participation.user_id = User.query.filter_by(username=request.form["user"]).first().id

    db.session.add(participation)
    db.session.commit()

    flash("Učešće uspešno zabeleženo", "Info")
    return redirect(url_for("aktivnosti.addAktivnost"))

# Kreiranje QR koda za izabranu aktivnost
@aktivnosti_bp.route("/aktivnosti/qr", methods=["POST"])
@login_required
def generateQR():
    aktivnostID = request.form["activity"]

    memory = BytesIO()
    link = url_for("aktivnosti.qr_log_aktivnost", _external=True, activityID = aktivnostID)
    img = qrcode.make(link)
    img.save(memory)
    memory.seek(0)

    base64_img = "data:image/ong;base64," + b64encode(memory.getvalue()).decode('ascii')

    if current_user.role == "admin":
        # admin odreda dodaje samo aktivnosti koje organizuje njegov odred
        activities = Activity.query.filter_by(organizer_name=current_user.odred.name).all()
    elif current_user.role == "savez_admin":
        # savez_admin dodaje aktivnosti koje organizuje savez ili neka od internacionalnih organinzacija
        activities = Activity.query.filter(Activity.organizer_type != OrganizerLevel(1))
    else:
        # Mogu da pristupe samo admini
        return redirect(url_for("dashboard.dashboard"))
    
    return render_template("addAktivnost.html",qrimg = base64_img,activities = activities)

# Dodeljivanje aktivnosti clanovima preko QR koda
@aktivnosti_bp.route("/aktivnosti/log/<int:activityID>", methods=["GET"])
@login_required
def qr_log_aktivnost(activityID):
    participation = Participation()

    participation.activity_id = activityID
    participation.user_id = current_user.id

    db.session.add(participation)
    db.session.commit()

    flash("Učešće uspešno zabeleženo", "Info")
    return redirect(url_for("aktivnosti.aktivnosti"))