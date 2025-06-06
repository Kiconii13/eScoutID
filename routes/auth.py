import datetime

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user, login_required

from models import db
from models.user import User

auth_bp = Blueprint('auth', __name__)


# Preusmeravanje ulogovanih i neulogovanih usera na login screen i na dashboard respektivno
@auth_bp.route('/')
def index():
    if current_user.is_anonymous:
        return render_template("index.html")
    else:
        return redirect(url_for("dashboard.dashboard"))


# Logovanje trenutnog usera, izvrsava se samo na index.html
@auth_bp.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # Collect info from the form
        username = request.form['username']
        password = request.form['password']

        # Check if it's in the db / login
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            user.authenticated = True
            login_user(user)
            user.last_login_date = datetime.datetime.now()
            return redirect(url_for("dashboard.dashboard"))
        # If False show index
        else:
            flash('Nepostojeća kombinacija korisničkog imena i lozinke!', 'Greška')
    return render_template("index.html")


# Logout
@auth_bp.route("/logout")
@login_required
def logout():
    user = current_user
    user.authenticated = False
    db.session.commit()

    logout_user()

    return redirect(url_for('auth.index'))
