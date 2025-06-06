from datetime import datetime

from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user


from models import User, db
from models.activity import Activity, Participation, OrganizerLevel

import qrcode
from io import BytesIO
from base64 import b64encode
import string
import random

from permissions import role_required

aktivnosti_bp = Blueprint('aktivnosti', __name__)


# Prikaz svih aktivnosti u kojima je ucestvovao ulogovani clan
@aktivnosti_bp.route("/aktivnosti")
@login_required
def aktivnosti():
    activities = Activity.query.order_by(Activity.id).all()

    return render_template("aktivnosti.html", activities=activities)


# Prikaz stranice za dodavanje i dodeljivanje aktivnosti
@aktivnosti_bp.route("/addAktivnost")
@login_required
@role_required("admin", "savez_admin")
def addAktivnost():
    if current_user.role == "admin":
        # admin odreda dodaje samo aktivnosti koje organizuje njegov odred
        activities = Activity.query.filter_by(organizer_name=current_user.odred.name).all()
    elif current_user.role == "savez_admin":
        # savez_admin dodaje aktivnosti koje organizuje savez ili neka od internacionalnih organinzacija
        activities = Activity.query.filter(Activity.organizer_type != OrganizerLevel(1))

    return render_template("addAktivnost.html", activities=activities)


# Dodavanje nove aktivnosti u bazu
@aktivnosti_bp.route("/aktivnosti/new", methods=["POST"])
@login_required
@role_required("admin", "savez_admin")
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
@role_required("admin", "savez_admin")
def log_aktivnost():
    participation = Participation()

    participation.activity_id = request.form["activity"]
    participation.user_id = User.query.filter_by(username=request.form["user"]).first().id

    #Provera da li je clanu vec zabelezeno ucesce na izabranoj aktivnosti
    activities = Participation.query.filter_by(user_id=participation.user_id).all()
    activity_ids = [str(activity.activity_id) for activity in activities]
    if participation.activity_id in activity_ids:
        flash("Ova aktivnost je već zabeležena za izabranog korisnika","Greška")
    else:
        db.session.add(participation)
        db.session.commit()
        flash("Učešće uspešno zabeleženo", "Info")
    
    return redirect(url_for("aktivnosti.addAktivnost"))


# Kreiranje QR koda za izabranu aktivnost
@aktivnosti_bp.route("/aktivnosti/qr", methods=["POST","GET"])
@login_required
@role_required("admin", "savez_admin")
def generateQR(activity):
    #Generisanje i dodeljivanje jedinstvenog stringa izabranoj aktivosti
    if activity.key is None:
        activity.key = ''.join(random.choices(string.ascii_letters,k=32))
        db.session.commit()
    url = url_for("aktivnosti.qr_log_aktivnost", _external=True,key=activity.key)

    memory = BytesIO()
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

    base64_img = "data:image/ong;base64," + b64encode(memory.getvalue()).decode('ascii')

    if current_user.role == "admin":
        # admin odreda dodaje samo aktivnosti koje organizuje njegov odred
        activities = Activity.query.filter_by(organizer_name=current_user.odred.name).all()
    elif current_user.role == "savez_admin":
        # savez_admin dodaje aktivnosti koje organizuje savez ili neka od internacionalnih organinzacija
        activities = Activity.query.filter(Activity.organizer_type != OrganizerLevel(1))

    return render_template("addAktivnost.html", qrimg=base64_img, activities=activities)


# Dodeljivanje aktivnosti clanovima preko QR koda
@aktivnosti_bp.route("/aktivnosti/log/<key>", methods=["GET"])
@login_required
def qr_log_aktivnost(key):
    participation = Participation()
    activity = Activity.query.filter_by(key=key).first()
    if activity is None:
        flash("Aktivnost ne postoji", "Greška")
        return redirect(url_for("aktivnosti.aktivnosti"))
    participation.activity_id = activity.id
    participation.user_id = current_user.id
    
    #Provera da li je clanu vec zabelezeno ucesce na izabranoj aktivnosti
    activities = Participation.query.filter_by(user_id=participation.user_id).all()
    activity_ids = [activity.activity_id for activity in activities]
    if participation.activity_id in activity_ids:
        flash("Ova aktivnost je već zabeležena za izabranog korisnika","Greška")
    else:
        db.session.add(participation)
        db.session.commit()
        flash("Učešće uspešno zabeleženo", "Info")
    
    return redirect(url_for("aktivnosti.aktivnosti"))

@aktivnosti_bp.route("/aktivnosti/delete", methods=["POST","GET"])
@login_required
def deleteAktivnost(activity):
    db.session.delete(activity)
    db.session.commit()
    return redirect(url_for("aktivnosti.addAktivnost"))

@aktivnosti_bp.route("/aktivnost/info")
@login_required
@role_required("admin", "savez_admin")
def info(activity):
    participants_ids = Participation.query.filter_by(activity_id=activity.id).all()
    participants = []
    for participation in participants_ids:
        user = User.query.filter_by(id=participation.user_id).first()
        if user:
            participants.append(user)
    return render_template("viewAktivnost.html", activity=activity, participants=participants)

@aktivnosti_bp.route("/handle_action", methods=["POST","GET"])
@login_required
@role_required("admin", "savez_admin")
def handle_action():
    action_type = request.form.get('action_type')
    activity_id = request.form.get('activity')
    user_username = request.form.get('user')

    # Proveri da li je izabrana aktivnost
    if not activity_id:
        flash('Molimo vas da izaberete aktivnost.', 'Greška')
        return redirect(url_for('aktivnosti.addAktivnost'))

    # Pronađi aktivnost
    activity = Activity.query.get(activity_id)

    # Akcija za beleženje učešća
    if action_type == 'log_aktivnost':
        if not user_username:
            flash('Molimo vas da unesete username člana.', 'Greška')
            return redirect(url_for('aktivnosti.addAktivnost'))

        user = User.query.filter_by(username=user_username).first()
        if user:
            participation = Participation.query.filter_by(activity_id=activity_id, user_id=user.id).first()
            if participation:
                flash('Ova aktivnost je već zabeležena za ovog korisnika.', 'Greška')
            else:
                new_participation = Participation(activity_id=activity_id, user_id=user.id)
                db.session.add(new_participation)
                db.session.commit()
                flash('Učešće uspešno zabeleženo.', 'Info')
        else:
            flash('Korisnik nije pronađen.', 'Greška')

        # Preusmeravanje na već postojeći 'log_aktivnost' route
        return redirect(url_for("aktivnosti.addAktivnost"))

    # Akcija za generisanje QR koda
    elif action_type == 'generate_qr':
        return generateQR(activity)

    # Akcija za brisanje aktivnosti
    elif action_type == 'delete_aktivnost':
        return deleteAktivnost(activity)

    # Akcija za prikaz informacija aktivnosti
    elif action_type == 'info_aktivnost':
        return info(activity)

    return redirect(url_for("aktivnosti.addAktivnost"))

