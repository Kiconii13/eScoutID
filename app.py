from flask import Flask, render_template, request, redirect, session, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "8PvUV36JVw59"

# Configure SQL Alchemy
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///eScoutID.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


# Database Model
class User(db.Model):
    # Class Variables
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), unique=True, nullable=False)
    password_hash = db.Column(db.String(150), nullable=False)
    password_salt = db.Column(db.String(32), nullable=False)
    role = db.Column(db.String(), default="clan")
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))


    def set_password(self, password):
        self.password_hash = generate_password_hash(password)


    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Odred(db.Model):
    # Class Variables
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    city = db.Column(db.String(50))
    address = db.Column(db.String(50))
    email = db.Column(db.String(50))
    founded_at = db.Column(db.Date)
    staresina_id = db.Column(db.Integer,db.ForeignKey("user.id"))
    nacelnik_id = db.Column(db.Integer,db.ForeignKey("user.id"))


@app.route('/')
def home():  # put application's code here
    if "username" in session:
        return redirect(url_for("dashboard"))
    return render_template("index.html")


# Login
@app.route('/login', methods=["POST"])
def login():
    # Collect info from the form
    username = request.form['username']
    password = request.form['password']

    # Check if it's in the db / login
    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        session['username'] = username
        return redirect(url_for("dashboard"))
    # If False show index
    else:
        return render_template("index.html")


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
def dashboard():
    if "username" in session:
        user = User.query.filter_by(username=session['username']).first()
        return render_template("dashboard.html", username=user.username)

@app.route("/edit", methods=["POST"])
def edit():
    if "username" in session:
        name = request.form['name']
        user = User.query.filter_by(username=session['username']).first()
        user.name = name
        db.session.commit()
        return render_template("dashboard.html", username=user.username)

# Logout
@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for('home'))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    
    app.run(debug=True)
