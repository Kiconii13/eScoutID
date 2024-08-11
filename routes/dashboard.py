from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user

from models import User, db

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template("dashboard.html")


# Promena lozinke; Mora se uneti trenutna lozinka i nova lozinka sa potvrdom.
@dashboard_bp.route('/dashboard/changePassword', methods=["POST", "GET"])
@login_required
def changePassword():
    if request.method == "POST":
        check_user = User()
        check_user.set_password(request.form["current_password"])
        # Provera da li se unesena lozinka poklapa sa trenutnom lozinkom
        if not current_user.check_password(request.form["current_password"]):
            flash("Niste uneli tačnu trenutnu lozinku!", "Greška")
            return redirect(url_for("dashboard.changePassword"))
        # Provera da li se nova lozinka poklapa sa potvrdom
        if request.form["new_password"] != request.form["new_password_check"]:
            flash("Nova lozinka i potvrda nove lozinke se ne poklapaju!", "Greška")
            return redirect(url_for("dashboard.changePassword"))
        # Uspešna promena
        current_user.set_password(request.form["new_password"])
        db.session.commit()
        flash("Uspešno ste promenili lozinku!", "info")
        return redirect(url_for("dashboard.dashboard"))
    else:
        return render_template("changePassword.html")

@dashboard_bp.route('/dashboard/changeUsername', methods=["POST", "GET"])
@login_required
def changeUsername():
    if request.method == "POST":
        if current_user.username != request.form["current_username"]:
            flash("Netačno trenutno korisničko ime!", "Greška")
            return redirect(url_for("dashboard.changeUsername"))
        if request.form["new_username"] != request.form["new_username_check"]:
            flash("Novo korisničko ime i potvrda novog korisničkog imena se ne poklapaju!", "Greška")
            return redirect(url_for("dashboard.changeUsername"))
        check_user = User.query.filter_by(username = request.form["new_username"]).first()
        if check_user:
            flash("Korisničko ime je već zauzeto", "Greška")
            return redirect(url_for("dashboard.changeUsername"))
        current_user.username = request.form["new_username"]
        db.session.commit()
        flash("Uspešno ste promenili korisničko ime!", "info")
        return redirect(url_for("dashboard.dashboard"))
    else:
        return render_template("changeUsername.html")
