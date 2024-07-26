from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user

from models import User, db

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template("dashboard.html")

@dashboard_bp.route('/dashboard/changePassword', methods=["POST","GET"])
@login_required
def changePassword():
    if request.method == "POST":
        check_user = User()
        check_user.set_password(request.form["current_password"])
        if not current_user.check_password(request.form["current_password"]):
            flash("Niste uneli tačnu trenutnu lozinku!", "greška")
            return redirect(url_for("dashboard.changePassword"))
        if request.form["new_password"] != request.form["new_password_check"]:
            flash("Nova lozinka i potvrda nove lozinke se ne poklapaju!", "greška")
            return redirect(url_for("dashboard.changePassword"))
        current_user.set_password(request.form["new_password"])
        db.session.commit()
        flash("Uspešno ste promenili lozinku!","info")
        return redirect(url_for("dashboard.dashboard"))
    else:
        return render_template("changePassword.html")