from flask import Blueprint, redirect, url_for, render_template, flash, request, make_response
from flask_login import login_required, current_user

from models import User, db, Odred

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
    return render_template("odredDashboard.html", odred_name=Odred.query.filter_by(id=id).first(), users=User.query.filter_by(odred_id=id).all())

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
        return redirect(url_for("odred.odredDashboard", id=current_user.odred.id))
    else:
        #Mogu da pristupe samo admini
        if current_user.role != "admin" and current_user.role != "savez_admin":
            return redirect(url_for("dashboard.dashboard"))
        return render_template("addClan.html", h1="Dodaj člana", action=action, clan=new_user)

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
        
        odred = Odred.query.filter_by(id=user.odred_id).first()
        return render_template("addClan.html", h1="Izmeni člana", action=action, clan=user, odred=odred.name)

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
