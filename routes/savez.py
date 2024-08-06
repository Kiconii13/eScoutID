from datetime import datetime

from flask import Blueprint, redirect, url_for, render_template, request, flash, make_response
from flask_login import current_user, login_required
from sqlalchemy import func

from models import db, Odred, User, Ceta, Vod

savez_bp = Blueprint('savez', __name__)


# Prikaz tabele sa svim odredima
@savez_bp.route("/savezDashboard")
@login_required
def savezDashboard():
    # Moze da pristupi samo savez_admin
    if current_user.role != "savez_admin":
        return redirect(url_for("dashboard.dashboard"))

    odredi = Odred.query.all()
    Broj_Clanova = []
    Broj_Clanarina = []
    for odred in odredi:
        broj_clanova = User.query.filter_by(odred_id = odred.id).count()
        Broj_Clanova.append(broj_clanova)
        broj_clanarina = User.query.filter_by(odred_id= odred.id, has_paid=True).count()
        Broj_Clanarina.append(broj_clanarina)
    return render_template("savezDashboard.html", odredi=zip(odredi, Broj_Clanova, Broj_Clanarina))


#  Dodavanje novog odreda u bazu
@savez_bp.route("/addOdred", methods=["POST", "GET"])
@login_required
def addOdred():
    if request.method == "POST":
        new_odred = Odred()
        new_odred.name = request.form["name"]
        new_odred.city = request.form["city"]
        new_odred.address = request.form["address"]
        new_odred.email = request.form["email"]
        new_odred.founded_at = datetime.fromisoformat(request.form["founded_at"]).date()
        new_odred.status = request.form.get('status')
        if request.form["image"] != "nochange":
            new_odred.avatar = request.form["image"]

        db.session.add(new_odred)
        db.session.commit()

        # Generisanje prve cete u odredu
        first_ceta = Ceta()
        first_ceta.name = "Četa"
        first_ceta.odred_id = new_odred.id
        db.session.add(first_ceta)
        db.session.commit()

        # Generisanje prvog voda u odredu
        first_vod = Vod()
        first_vod.name = "Vod"
        first_vod.ceta_id = first_ceta.id
        db.session.add(first_vod)
        db.session.commit()

        #  Generisanje prvog clana u odredu; Preko njega se dodaje par clanova dodeljuje se novi admin i onda se brise iz baze.
        first_user = User()
        first_user.username = "Generic" + str(new_odred.id)
        first_user.role = "admin"
        first_user.odred_id = new_odred.id
        first_user.vod_id = first_vod.id
        first_user.set_password("generic")
        first_user.first_name = "Generic"
        first_user.last_name = "Generic"
        db.session.add(first_user)
        db.session.commit()

        new_odred.nacelnik_id = first_user.id
        new_odred.staresina_id = first_user.id
        first_vod.vodnik_id = first_user.id
        first_ceta.vodja_id = first_user.id
        db.session.commit()

        return redirect(url_for("savez.savezDashboard"))
    else:
        # Moze da pristupi samo savez_admin
        if current_user.role != "savez_admin":
            return redirect(url_for("dashboard.dashboard"))
        return render_template("addOdred.html", h1="Dodaj odred", odred=Odred(), staresina="", nacelnik="")


@savez_bp.route("/odred/avatar/<int:id>")
@login_required
def getPfp(id):
    # Mogu da pristupe samo admini
    if current_user.role != "admin" and current_user.role != "savez_admin":
        return redirect(url_for("dashboard.dashboard"))

    odred = Odred.query.filter_by(id=id).first()
    if odred.avatar:
        response = make_response(odred.avatar, 200)
    else:
        response = make_response("default", 200)
    response.mimetype = "text/plain"
    return response


# Izmena podataka postojeceg odreda
@savez_bp.route("/editOdred/<int:id>", methods=["POST", "GET"])
@login_required
def editOdred(id):
    odred = Odred.query.get(id)
    if request.method == "POST":
        odred.name = request.form["name"]
        odred.city = request.form["city"]
        odred.address = request.form["address"]
        odred.email = request.form["email"]
        odred.founded_at = datetime.fromisoformat(request.form["founded_at"]).date()
        staresina = User.query.filter_by(username=request.form.get("staresina_username")).first()
        if (not staresina) or staresina.odred_id != odred.id:
            flash("Nepostoji član odreda sa tim usernameom (starešina)")
            return redirect(url_for("savez.editOdred", id=odred.id))
        odred.staresina_id = staresina.id
        nacelnik = User.query.filter_by(username=request.form.get("nacelnik_username")).first()
        if (not nacelnik) or nacelnik.odred_id != odred.id:
            flash("Nepostoji član odreda sa tim usernameom (načelnik)")
            return redirect(url_for("savez.editOdred", id=odred.id))
        odred.nacelnik_id = nacelnik.id
        odred.status = request.form.get('status')
        if request.form["image"] != "nochange":
            odred.avatar = request.form["image"]
        db.session.commit()
        return redirect(url_for("savez.savezDashboard"))
    else:
        # Moze da pristupi samo savez_admin
        if current_user.role != "savez_admin":
            return redirect(url_for("dashboard.dashboard"))
        return render_template("addOdred.html", h1="Izmeni odred", odred=odred,
                               clanovi=User.query.filter_by(odred_id=odred.id).order_by(User.dob.asc()))


# Brisanje odreda iz baze
@savez_bp.route("/deleteOdred/<int:id>", methods=["GET", "POST"])
@login_required
def deleteOdred(id):
    # Moze da pristupi samo savez_admin
    if current_user.role != "savez_admin":
        return redirect(url_for("dashboard.dashboard"))

    odred = Odred.query.get(id)
    if odred:
        db.session.delete(odred)
        db.session.commit()
        flash("Odred je uspešno obrisan.", "success")
    else:
        flash("Odred nije pronađen.", "error")
    return redirect(url_for("savez.savezDashboard"))
