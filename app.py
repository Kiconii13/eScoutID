from flask import Flask, render_template, request, redirect, session, url_for, flash

from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user

from models import db
from models import User, Odred

app = Flask(__name__)
app.secret_key = "8PvUV36JVw59"

# Configure SQL Alchemy
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///eScoutID.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(id = user_id).first()


@app.route('/')
def index():
    if current_user.is_anonymous:
        return render_template("index.html")
    else:
        return redirect(url_for("dashboard"))


@app.route('/login', methods=["GET","POST"])
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
            return redirect(url_for("dashboard"))
        # If False show index
        else:
            flash('Nepostojeća kombinacija korisničkog imena i lozinke!', 'Greška')
    return render_template("index.html")

# Logout
@app.route("/logout")
@login_required
def logout():
    # session.pop("username", None)
    user = current_user
    user.authenticated = False
    db.session.commit()

    logout_user()

    return redirect(url_for('index'))

# Register
@app.route("/register", methods=["POST"])
def register():
    # Collect info from the form
    username = request.form['username']
    password = request.form['password']

    # Check if it's in the db / index
    user = User.query.filter_by(username=username).first()

    if user:
        return render_template("index.html", error="Already registered!")
    else:
        new_user = User(username=username)
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()

        session["username"] = username
        return redirect(url_for("dashboard"))


# Dashboard
@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")


@app.route("/odred")
@login_required
def odred():
    flash("Work in progress", "Info")
    return render_template("odred.html")

@app.route("/edit", methods=["POST"])
@login_required
def edit():
    # if "username" in session:
    name = request.form['name']

    user = User.query.filter_by(username=session['username']).first()
    user.name = name
    
    db.session.commit()
    
    return render_template("dashboard.html", username=user.username)




if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    
    app.run(debug=True)
