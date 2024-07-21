from eScoutID import app
from flask import render_template, redirect, session, url_for, request
from eScoutID.models import User, db, get_by_username, add_new_user, edit_name, get_users


@app.route('/')
def home():  # put application's code here
    if "username" in session:
        user = get_by_username(session['username'])
        if user.role == "clan":
            return redirect(url_for("dashboard"))
        elif user.role == "odred":
            return redirect(url_for("odredDashboard"))
    return render_template("Index.html")


# Login
@app.route('/login', methods=["POST"])
def login():
    # Collect info from the form
    username = request.form['username']
    password = request.form['password']

    # Check if it's in the db / login
    user = get_by_username(username)
    if user and user.check_password(password):
        session['username'] = username
        if user.role == "clan":
            return redirect(url_for("dashboard"))
        elif user.role == "odred":
            return redirect(url_for("odredDashboard"))
    # If False show index
    else:
        return render_template("Index.html")


# Register
@app.route("/register", methods=["POST"])
def register():
    # Collect info from the form
    username = request.form['username']
    password = request.form['password']

    # Check if it's in the db / index
    user = get_by_username(username)
    if user:
        return render_template("Index.html", error="Already registered!")
    else:
        new_user = User.username_only(username)
        new_user.set_password(password)
        add_new_user(new_user.username,new_user.password_hash)
        session["username"] = username
        return redirect(url_for("dashboard"))


# Dashboard
@app.route("/dashboard")
def dashboard():
    if "username" in session:
        user = get_by_username(session["username"])
        return render_template("dashboard.html", username=user.username)


@app.route("/edit", methods=["POST"])
def edit():
    if "username" in session:
        name = request.form['name']
        user = get_by_username(session["username"])
        edit_name(name, user.username)
        return render_template("dashboard.html", username=user.username)


@app.route("/odredDashboard")
def odredDashboard():
    if "username" in session:
        odred = get_by_username(session['username'])
        users = get_users(odred.id)
        return render_template("OdredDashboard.html", users=users)


# Logout
@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for('home'))
