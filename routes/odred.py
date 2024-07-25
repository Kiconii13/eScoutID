from sqlalchemy.exc import IntegrityError

from flask import Blueprint, redirect, url_for, render_template, flash, request, make_response
from flask_login import login_required, current_user

from models import User, db, Odred

odred_bp = Blueprint("odred", __name__)


@odred_bp.route("/odredDashboard/<int:id>")
@login_required
def odredDashboard(id):
    if current_user.role != "admin" and current_user.role != "savez_admin":
        return redirect(url_for("dashboard.dashboard"))
    return render_template("odredDashboard.html",odred_name=Odred.query.filter_by(id=id).first(), users=User.query.filter_by(odred_id=id).all())

@odred_bp.route("/addClan", methods=["POST", "GET"])
@login_required
def addClan():
    new_user = User()
    if request.method == "POST":
        try:
            # UPIS NOVOG CLANA U BAZU
            new_user = User.defUser(new_user)
            new_user.password = User.set_password(new_user, request.form["password"])
            new_user.odred_id = current_user.odred_id
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for("odred.odredDashboard", id=current_user.odred.id))
        except IntegrityError:  # exeption ako korisnicko ime vec postoji (Mogo bi malo drugacije da se napravi ispis greske, funkcionalnost je tu)
            db.session.rollback()
            flash("Uneto korisničko ime već postoji!", "Greška")
            return render_template("addClan.html", h1="Dodaj člana", clan=User())
    else:
        if current_user.role != "admin":
            return redirect(url_for("dasboard.dashboard"))
        return render_template("addClan.html", h1="Dodaj člana", clan=new_user)


@odred_bp.route("/editClan/<int:id>", methods=["POST", "GET"])
@login_required
def editClan(id):
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
            return render_template("addClan.html", h1="Izmeničlana", clan=User.query.get(id))
    else:
        if current_user.role != "admin":
            return redirect(url_for("dashboard.dashboard"))
        odred = Odred.query.filter_by(id=user.odred_id).first()
        return render_template("addClan.html", h1="Izmeni člana", clan=user, odred=odred.name)

@odred_bp.route("/deleteClan/<int:id>", methods=["GET", "POST"])
@login_required
def deleteClan(id):
    user = User.query.get(id)
    if user:
        db.session.delete(user)
        db.session.commit()
        flash("Član je uspešno obrisan.", "success")
    else:
        flash("Član nije pronađen.", "error")
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
