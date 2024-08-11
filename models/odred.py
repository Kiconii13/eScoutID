from . import db, User
from datetime import datetime


class Odred(db.Model):
    __tablename__ = 'odred'

    # Class Variables
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    city = db.Column(db.String(50))
    address = db.Column(db.String(50))
    email = db.Column(db.String(50))
    founded_at = db.Column(db.Date(), default=datetime.today().date())
    status = db.Column(db.String(11), default="Pridružen")
    avatar = db.Column(db.Text, default="")

    staresina_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    staresina = db.relationship('User', foreign_keys=[staresina_id])

    nacelnik_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    nacelnik = db.relationship('User', foreign_keys=[nacelnik_id])

    members = db.relationship('User', back_populates='odred',foreign_keys=[User.odred_id])

    def __init__(self, name="", city="", address="", email="", founded_at=datetime.today().date(), staresina_id=None,
                 nacelnik_id=None, status="Pridružen"):
        self.name = name
        self.city = city
        self.address = address
        self.email = email
        self.founded_at = founded_at
        self.staresina_id = staresina_id
        self.nacelnik_id = nacelnik_id
        self.status = status

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"<Odred {self.name}>"
