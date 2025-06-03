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
    jmbg = db.Column(db.String(13), unique=True, nullable=True)
    dob = db.Column(db.Date, default=datetime.today().date())
    join_date = db.Column(db.Date, default=datetime.today().date())
    phone_number = db.Column(db.String(13), default="")
    email = db.Column(db.String(100), default="")
    address = db.Column(db.String(100), default="")
    scout_id_number = db.Column(db.String(20), unique=True, nullable=True)
    account_creation_date = db.Column(db.DateTime, default=datetime.utcnow)
    gender = db.Column(db.String(10), nullable=True)
    last_login_date = db.Column(db.DateTime, nullable=True)
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
    skills = db.relationship("Skill", back_populates="user", cascade="all, delete-orphan")

    def calculate_gender(self):
        # Ekstraktovanje cifara od 10. do 12. iz JMBG-a
        pol_cifre = int(self.jmbg[9:12])

        # Određivanje pola
        if pol_cifre < 500:
            self.gender = "M"
        else:
            self.gender = "Z"

    def extract_birth_date(self):
        # Prve dve cifre su dan rođenja
        day = int(self.jmbg[0:2])
        # Sledeće dve cifre su mesec rođenja
        month = int(self.jmbg[2:4])
        # Sledeće tri cifre su godina rođenja
        year = int(self.jmbg[4:7])

        # Godina rođenja: 0xx za 2000-te, 1xx za 1000-te, 9xx za 1900-te
        if year < 100:
            year += 2000
        else:
            year += 1000

        # Kreiramo datum rođenja
        self.dob = datetime(year, month, day)


    def defUser(user):
        user.first_name = request.form["first_name"]
        user.last_name = request.form["last_name"]
        user.jmbg = request.form["jmbg"]
        user.role = request.form.get("role")
        user.extract_birth_date()
        user.calculate_gender()
        user.join_date = datetime.fromisoformat(request.form["join_date"]).date()
        user.phone_number = request.form["phone_number"]
        user.scout_id_number = request.form["scout_id_number"]
        user.email = request.form["email"]
        user.address = request.form["address"]
        user.has_paid = 1 if request.form.get('has_paid') else 0
        user.vod_id = request.form["vod"]
        # if request.form["fileInput"] != "nochange":
        #     user.avatar = request.form["fileInput"]
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
