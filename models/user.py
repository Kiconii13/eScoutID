from flask import request

from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

from datetime import datetime


class User(db.Model, UserMixin):
    __tablename__ = "users"

    # Class Variables
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), unique=True, nullable=False, default="")
    password_hash = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(16), default="clan")

    first_name = db.Column(db.String(50), default="")
    last_name = db.Column(db.String(50), default="")
    dob = db.Column(db.Date, default=datetime.today().date())
    join_date = db.Column(db.Date, default=datetime.today().date())
    phone_number = db.Column(db.String(12), default="")
    email = db.Column(db.String(100), default="")
    address = db.Column(db.String(100), default="")

    has_paid = db.Column(db.Boolean(), default=False)
    jedinica = db.Column(db.String(30), default="")

    odred_id = db.Column(db.Integer, db.ForeignKey("odred.id"))
    odred = db.relationship('Odred', back_populates='members', foreign_keys=[odred_id])

    # konstruktor za default vrednosti da ne budu None
    def __init__(self, username="", role="clan", first_name="", last_name="", dob=datetime.today().date(),
                 join_date=datetime.today().date(), phone_number="", email="", adress="", has_paid=False, jedinica=""):
        self.username = username
        self.role = role
        self.first_name = first_name
        self.last_name = last_name
        self.dob = dob
        self.join_date = join_date
        self.phone_number = phone_number
        self.email = email
        self.address = adress
        self.has_paid = has_paid
        self.jedinica = jedinica

    activities = db.relationship('Activity', secondary='participations', back_populates='participants')

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

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return str(self.id)

    @property
    def is_active(self):
        # Optional: Implement if you have an activation process for users
        return True

    @property
    def is_authenticated(self):
        return True  # Assuming all users are authenticated

    @property
    def is_anonymous(self):
        return False

    @staticmethod
    def get(user_id):
        return User.query.get(int(user_id))

    def __repr__(self):
        return f"<User {self.id}>"
