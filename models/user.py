from flask import request

from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

from datetime import datetime
from random import randint


class User(db.Model, UserMixin):
    __tablename__ = "users"

    # Class Variables
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), unique=True, nullable=False, default="")
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(16), default="clan")

    first_name = db.Column(db.String(50), default="")
    last_name = db.Column(db.String(50), default="")
    dob = db.Column(db.Date, default=datetime.today().date())
    join_date = db.Column(db.Date, default=datetime.today().date())
    phone_number = db.Column(db.String(12), default="")
    email = db.Column(db.String(100), default="")
    address = db.Column(db.String(100), default="")
    avatar = db.Column(db.Text, default="")

    has_paid = db.Column(db.Boolean(), default=False)
    jedinica = db.Column(db.String(30), default="")

    let_level = db.Column(db.Integer(), default=0)
    zvezda_level = db.Column(db.Integer(), default=0)
    krin_level = db.Column(db.Integer(), default=0)

    odred_id = db.Column(db.Integer, db.ForeignKey("odred.id"))
    odred = db.relationship('Odred', back_populates='members', foreign_keys=[odred_id])

    vod_id = db.Column(db.Integer, db.ForeignKey("vod.id"))
    vod = db.relationship('Vod', back_populates='members', foreign_keys=[vod_id])

    activities = db.relationship('Activity', secondary='participations', back_populates='participants')

    def defUser(user):
        user.first_name = request.form["first_name"]
        user.last_name = request.form["last_name"]
        user.role = request.form.get("role")
        user.dob = datetime.fromisoformat(request.form["dob"]).date()
        user.join_date = datetime.fromisoformat(request.form["join_date"]).date()
        user.phone_number = request.form["phone_number"]
        user.email = request.form["email"]
        user.address = request.form["address"]
        user.has_paid = 1 if request.form.get('has_paid') else 0
        user.vod_id = request.form["vod"]
        if request.form["image"] != "nochange":
            user.avatar = request.form["image"]
        if not user.username:
            user.username = f"{user.last_name[0].lower()}{user.first_name[0].lower()}.{randint(1000, 9999)}"
        return user

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return str(self.id)

    @property
    def is_active(self):
        return True

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    @staticmethod
    def get(user_id):
        return User.query.get(int(user_id))

    def __repr__(self):
        return f"<User {self.id}>"
