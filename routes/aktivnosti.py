from datetime import datetime

from flask import Blueprint, render_template, flash, redirect, url_for, request, current_app
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
    current_app.logger.log(25, f"{current_user.role} odreda {current_user.odred.name}, {current_user.first_name} {current_user.last_name}, je dodao aktivnost \"{aktivnost.name}\" (id: {aktivnost.id})")
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

    activity = Activity.query.filter_by(id=participation.activity_id).first().name
    clan = User.query.filter_by(id=participation.user_id).first()

    flash("Učešće uspešno zabeleženo", "Info")
    current_app.logger.log(25, f"{current_user.role} odreda {current_user.odred.name}, {current_user.first_name} {current_user.last_name}, je zabeležio učešče člana \"{clan.first_name} {clan.last_name}\" (id: {participation.user_id}) na aktivnosti \"{activity}\" (id: {participation.activity_id})")
    return redirect(url_for("aktivnosti.addAktivnost"))

# Kreiranje QR koda za izabranu aktivnost
@aktivnosti_bp.route("/aktivnosti/qr", methods=["POST"])
@login_required
def generateQR():
    if current_user.role == "clan":
        return redirect(url_for("dashboard.dashboard"))

    aktivnostID = request.form["activity"]

    memory = BytesIO()
    url = url_for("aktivnosti.qr_log_aktivnost", _external=True, _scheme='https', activityID = activityID)
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=40,
        border=2
    )
    qr.add_data(url)
    qr.make(fit=True)
    qrimg = qr.make_image()
    qrimg.save(memory)
    memory.seek(0)

    base64_img = "data:image/png;base64," + b64encode(memory.getvalue()).decode('ascii')

    if current_user.role == "admin":
        # admin odreda dodaje samo aktivnosti koje organizuje njegov odred
        activities = Activity.query.filter_by(organizer_name=current_user.odred.name).all()
    elif current_user.role == "savez_admin":
        # savez_admin dodaje aktivnosti koje organizuje savez ili neka od internacionalnih organinzacija
        activities = Activity.query.filter(Activity.organizer_type != OrganizerLevel(1))
    
    return render_template("addAktivnost.html", qrimg = base64_img, activities = activities)

# Dodeljivanje aktivnosti clanovima preko QR koda
@aktivnosti_bp.route("/aktivnosti/log/<int:activityID>", methods=["GET"])
@login_required
def qr_log_aktivnost(activityID):
    participation = Participation()

    participation.activity_id = activityID
    participation.user_id = current_user.id

    db.session.add(participation)
    db.session.commit()

    activity = Activity.query.filter_by(id=participation.activity_id).first().name
    clan = User.query.filter_by(id=participation.user_id).first()

    flash("Učešće uspešno zabeleženo", "Info")
    current_app.logger.log(25, f"Na aktivnost {activity} se prijavio član {clan.first_name} {clan.last_name} pomoću QR koda (ili direktnog linka)")
    return redirect(url_for("aktivnosti.aktivnosti"))