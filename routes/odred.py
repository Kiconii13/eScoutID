from flask import Blueprint, redirect, url_for, render_template, flash, request, make_response
from flask_login import login_required, current_user

from models import User, db, Odred, Ceta, Vod

odred_bp = Blueprint("odred", __name__)

#Prikaz podataka o odredu
@odred_bp.route("/odred")
@login_required
def odred():
    try:
        Broj_Clanova = User.query.filter_by(odred_id=current_user.odred_id).count()
        return render_template("odred.html", broj_clanova=Broj_Clanova)
    except:
        flash("Morate biti član odreda!", "Greška")
        return redirect(url_for("dashboard.dashboard"))

#Prikaz tabele sa svim clanovima; Prikazuju se samo clanovi odreda ciji je admin trenutno ulogovani korisnik.
@odred_bp.route("/odredDashboard/<int:id>")
@login_required
def odredDashboard(id):
    #Mogu da pristupe samo admini
    if current_user.role == "clan":
        return redirect(url_for("dashboard.dashboard"))
    return render_template("odredDashboard.html", odred_name=Odred.query.filter_by(id=id).first(), users=User.query.filter_by(odred_id=id).all(), cete = Ceta.query.filter_by(odred_id=id).all())

#Dodavanje novog clana u odred
@odred_bp.route("/clan/add", methods=["POST", "GET"])
@login_required
def addClan():
    action = "add"
    new_user = User()
    if request.method == "POST":
        new_user = User.defUser(new_user)

        new_user.set_password(new_user.username)
        new_user.odred_id = current_user.odred_id

        db.session.add(new_user)
        db.session.commit()
        new_user.username = f"{new_user.username}{new_user.id}c"
        db.session.commit()
        return redirect(url_for("odred.odredDashboard", id=current_user.odred.id))
    else:
        #Mogu da pristupe samo admini
        if current_user.role != "admin" and current_user.role != "savez_admin":
            return redirect(url_for("dashboard.dashboard"))
        cetas = Ceta.query.filter_by(odred_id=current_user.odred_id).all()
        ceta_ids = [ceta.id for ceta in cetas]
        vods = Vod.query.filter(Vod.ceta_id.in_(ceta_ids)).all()
        return render_template("addClan.html", h1="Dodaj člana", action=action, clan=new_user, vods = vods)

#Izmene podataka vec postojeceg clana odreda
@odred_bp.route("/clan/edit/<int:id>", methods=["POST", "GET"])
@login_required
def editClan(id):
    action = "edit"
    user = User.query.get(id)
    if request.method == "POST":
        user = User.defUser(user)

        db.session.commit()
        return redirect(url_for("odred.odredDashboard", id=current_user.odred.id))
    else:
        #Mogu da pristupe samo admini
        if current_user.role != "admin" and current_user.role != "savez_admin":
            return redirect(url_for("dashboard.dashboard"))

        cetas = Ceta.query.filter_by(odred_id=current_user.odred_id).all()
        ceta_ids = [ceta.id for ceta in cetas]
        vods = Vod.query.filter(Vod.ceta_id.in_(ceta_ids)).all()
        return render_template("addClan.html", h1="Izmeni člana", action=action, clan=user, odred=Odred.query.filter_by(id=user.odred_id).first().name, vods = vods)

#Uklanjanje clana iz odreda
@odred_bp.route("/clan/delete/<int:id>", methods=["GET", "POST"])
@login_required
def deleteClan(id):
    #Mogu da pristupe samo admini
    if current_user.role != "admin" and current_user.role != "savez_admin":
        return redirect(url_for("dashboard.dashboard"))

    user = User.query.get(id)
    if user:
        db.session.delete(user)
        db.session.commit()
        flash("Član je uspešno obrisan.", "Info")
    else:
        flash("Član nije pronađen.", "Greška")
    return redirect(url_for("odred.odredDashboard", id=current_user.odred.id))

#Pretraga avatara korisnika
@odred_bp.route("/clan/avatar/<int:id>")
@login_required
def getPfp(id):
    #Mogu da pristupe samo admini
    if current_user.role != "admin" and current_user.role != "savez_admin":
        return redirect(url_for("dashboard.dashboard"))
    
    user = User.query.filter_by(id=id).first()
    if user.avatar:
        response = make_response(user.avatar, 200)
    else:
        response = make_response("default", 200)
    response.mimetype = "text/plain"
    return response


@odred_bp.route("/cv/add", methods=["GET", "POST"])
@login_required
def addCetaVod():
    return render_template("addCetaVod.html", users=User.query.filter_by(odred_id = current_user.odred_id).all(), cetas=Ceta.query.filter_by(odred_id = current_user.odred_id).all())


@odred_bp.route("/ceta/new", methods=["POST"])
@login_required
def newCeta():
    ceta = Ceta()

    ceta.name = request.form["name"]
    cete = Ceta.query.filter_by(odred_id = current_user.odred.id).all()
    if any(existing_ceta.name == ceta.name for existing_ceta in cete):
        flash("Četa sa tim imenom već postoji u odredu!", "Greška")
        return redirect(url_for("odred.addCetaVod"))
    db.session.add(ceta)
    db.session.commit()

    flash("Četa uspešno dodata!", "Info")
    return redirect(url_for("odred.addCetaVod"))

@odred_bp.route("/vod/new", methods=["POST"])
@login_required
def newVod():
    vod = Vod()

    vod.name = request.form["name"]
    vod.vodnik_id = request.form["vodnik"]
    vod.ceta_id = request.form["ceta"]

    db.session.add(vod)
    db.session.commit()

    flash("Vod uspešno dodat!", "Info")
    return redirect(url_for("odred.addCetaVod"))


@odred_bp.route("/edit/roles")
@login_required
def editRoles():
    cetas = Ceta.query.filter_by(odred_id=current_user.odred_id).all()
    ceta_ids = [ceta.id for ceta in cetas]
    vods = Vod.query.filter(Vod.ceta_id.in_(ceta_ids)).all()
    users = User.query.filter_by(odred_id=current_user.odred_id).order_by(User.dob.asc()).all()

    return render_template("editRoles.html", vods=vods, users=users, cetas=cetas, current_staresina = current_user.odred.staresina.id, current_nacelnik = current_user.odred.nacelnik.id)


@odred_bp.route("/edit/roles/vodnik", methods=["POST"])
@login_required
def editVodnik():
    vod = Vod.query.filter_by(id=request.form["vod"]).first()

    vod.vodnik_id = request.form["vodnik"]

    db.session.commit()

    flash("Novi vodnik postavljen", "Info")
    return redirect(url_for("odred.editRoles"))


@odred_bp.route("/edit/roles/vodjacete", methods=["POST"])
@login_required
def editVodjacete():
    ceta = Ceta.query.filter_by(id = request.form["ceta"]).first()

    ceta.vodja_id = request.form["vodjacete"]

    db.session.commit()

    flash("Novi vođa čete postavljen", "Info")
    return redirect(url_for("odred.editRoles"))


@odred_bp.route("/edit/nacelnik", methods=["POST"])
@login_required
def editNacelnikStaresina():

    current_user.odred.staresina_id = request.form["staresina"]
    current_user.odred.nacelnik_id = request.form["nacelnik"]

    db.session.commit()

    flash("Načelnik i starešina uspešno ažurirani", "Info")
    return redirect(url_for("odred.editRoles"))
