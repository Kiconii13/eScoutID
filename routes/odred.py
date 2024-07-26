from sqlalchemy.exc import IntegrityError

from flask import Blueprint, redirect, url_for, render_template, flash, request, make_response
from flask_login import login_required, current_user

from models import User, db, Odred

odred_bp = Blueprint("odred", __name__)


@odred_bp.route("/odred")
@login_required
def odred():
    try:
        Broj_Clanova = User.query.filter_by(odred_id=current_user.odred_id).count()
        return render_template("odred.html", broj_clanova=Broj_Clanova)
    except:
        flash("Morate biti član odreda!", "Greška")
        return redirect(url_for("dashboard.dashboard"))


@odred_bp.route("/odredDashboard/<int:id>")
@login_required
def odredDashboard(id):
    if current_user.role == "clan":
        return redirect(url_for("dashboard.dashboard"))
    return render_template("odredDashboard.html", odred_name=Odred.query.filter_by(id=id).first(), users=User.query.filter_by(odred_id=id).all())


@odred_bp.route("/clan/add", methods=["POST", "GET"])
@login_required
def addClan():
    action = "add"
    new_user = User()
    if request.method == "POST":
        try:
            # UPIS NOVOG CLANA U BAZU
            new_user = User.defUser(new_user)

            new_user.set_password(new_user.username)
            
            new_user.odred_id = current_user.odred_id

            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for("odred.odredDashboard", id=current_user.odred.id))
        except IntegrityError:  # exeption ako korisnicko ime vec postoji (Mogao bi malo drugacije da se napravi ispis greske, funkcionalnost je tu)
            db.session.rollback()
            flash("Uneto korisničko ime već postoji!", "Greška")
            return render_template("addClan.html", h1 = "Dodaj člana", action = action, clan = User())
    else:
        if current_user.role != "admin":
            return redirect(url_for("dashboard.dashboard"))
        return render_template("addClan.html", h1 = "Dodaj člana", action = action, clan = new_user)


@odred_bp.route("/clan/edit/<int:id>", methods=["POST", "GET"])
@login_required
def editClan(id):
    action = "edit"
    user = User.query.get(id)
    if request.method == "POST":
        try:
            # AZURIRANJE PODATAKA CLANA
            user = User.defUser(user)
            db.session.commit()
            return redirect(url_for("odred.odredDashboard", id = current_user.odred.id))
        except IntegrityError:  # exeption ako korisnicko ime vec postoji (Mogo bi malo drugacije da se napravi ispis greske, funkcionalnost je tu)
            db.session.rollback()
            flash("Uneto korisničko ime već postoji!", "Greška")
            return render_template("addClan.html", h1 = "Izmeni člana", action = action, clan = User.query.get(id))
    else:
        if current_user.role != "admin":
            return redirect(url_for("dashboard.dashboard"))
        odred = Odred.query.filter_by(id=user.odred_id).first()
        return render_template("addClan.html", h1 = "Izmeni člana", action = action, clan = user, odred = odred.name)


@odred_bp.route("/clan/delete/<int:id>", methods=["GET", "POST"])
@login_required
def deleteClan(id):
    user = User.query.get(id)
    if user:
        db.session.delete(user)
        db.session.commit()
        flash("Član je uspešno obrisan.", "Info")
    else:
        flash("Član nije pronađen.", "Greška")
    return redirect(url_for("odred.odredDashboard", id = current_user.odred.id))


@odred_bp.route("/clan/avatar/<int:id>")
@login_required
def getPfp(id):
    user = User.query.filter_by(id=id).first()
    if user.avatar:
        response = make_response(user.avatar, 200)
    else:
        response = make_response("default", 200)
    response.mimetype = "text/plain"
    return response
