from flask import Blueprint, render_template, flash, redirect, url_for
from flask_login import login_required, current_user

from models import User

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template("dashboard.html")


@dashboard_bp.route("/odred")
@login_required
def odred():
    try:
        Broj_Clanova = User.query.filter_by(odred_id=current_user.odred_id).count()
        return render_template("odred.html", broj_clanova=Broj_Clanova)
    except:
        flash("Morate biti član odreda!", "Greška")
        return redirect(url_for("dashboard.dashboard"))
