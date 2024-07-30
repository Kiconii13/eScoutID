from . import db, User
from datetime import datetime


class Ceta(db.Model):
    __tablename__ = 'ceta'

    # Class Variables
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    odred_id = db.Column(db.Integer, db.ForeignKey("odred.id"))

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"<Vod {self.name}>"
