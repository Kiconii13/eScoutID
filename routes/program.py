from flask import Blueprint, flash, render_template
from flask_login import login_required

program_bp = Blueprint('program', __name__)


@program_bp.route("/program")
@login_required
def program():
    flash("Work in progress", "info")
    return render_template("program.html")
