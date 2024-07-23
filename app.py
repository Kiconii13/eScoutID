from flask import Flask, render_template, request, redirect, session, url_for, flash
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from sqlalchemy.exc import IntegrityError

from models import db
from models import User, Odred
from datetime import datetime

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
        user = User.query.filter_by(username = username).first()
        
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
    user = User.query.filter_by(username = username).first()

    if user:
        return render_template("index.html", error="Already registered!")
    else:
        new_user = User(username = username)
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()

        session["username"] = username
        return redirect(url_for("index"))


# Dashboard
@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")


@app.route("/odred")
@login_required
def odred():
    Broj_Clanova=User.query.filter_by(odred_id = current_user.odred_id).count()
    return render_template("odred.html", broj_clanova = Broj_Clanova)

@app.route("/odreddashboard")
@login_required
def odreddashboard():
    return render_template("odredDashboard.html",users = User.query.filter_by(odred_id = current_user.odred_id).all())

#konstruktor mozda je bolje da bude u klasi
def defUser(user):
    user.username = request.form["username"]
    user.first_name = request.form["first_name"]
    user.last_name = request.form["last_name"]
    user.role = request.form.get("role")
    user.dob = datetime.fromisoformat(request.form["dob"]).date()
    user.join_date = datetime.fromisoformat(request.form["join_date"]).date()
    user.phone_number = request.form["phone_number"]
    user.email = request.form["email"]
    user.address = request.form["address"]
    user.has_paid = 1 if request.form.get('has_paid') else 0
    user.jedinica = request.form["jedinica"]
    return user

@app.route("/add", methods = ["POST","GET"])
@login_required
def add():
    new_user = User()
    if request.method == "POST":
        try:
            #UPIS U BAZU
            new_user = defUser(new_user)
            new_user.password = User.set_password(new_user, request.form["password"])
            new_user.odred_id = current_user.odred_id
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for("odreddashboard"))
        except IntegrityError: #exeption ako korisnicko ime vec postoji (Mogo bi malo drugacije da se napravi ispis greske, funkcionalnost je tu)
            db.session.rollback()
            flash("Uneto korisnicko ime vec postoji!","Los unos")
            return render_template("addClan.html", h1 = "Dodaj", clan = User())
    else:
        return render_template("addClan.html", h1 = "Dodaj", clan = new_user)

@app.route("/edit/<int:id>", methods = ["POST","GET"])
@login_required
def edit(id):
    user = User.query.get(id)
    if request.method == "POST":
        try:
            #AZURIRANJE PODATAKA
            user = defUser(user)
            db.session.commit()
            return redirect(url_for("odreddashboard"))
        except IntegrityError: #exeption ako korisnicko ime vec postoji (Mogo bi malo drugacije da se napravi ispis greske, funkcionalnost je tu)
            db.session.rollback()
            flash("Uneto korisnicko ime vec postoji!","Los unos")
            return render_template("addClan.html", h1 = "Izmeni", clan = User.query.get(id))
    else:
        return render_template("addClan.html", h1 = "Izmeni", clan = user)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    
    app.run(debug=True)
