from . import db, User, ceta
from datetime import datetime


class Vod(db.Model):
    __tablename__ = 'vod'

    # Class Variables
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    vodnik_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    ceta_id = db.Column(db.Integer, db.ForeignKey("ceta.id"))

    members = db.relationship('User', back_populates='vod', foreign_keys=[User.vod_id])

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"<Vod {self.name}>"

