from . import db, User

class Odred(db.Model):
    __tablename__ = 'odred'

    # Class Variables
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    city = db.Column(db.String(50))
    address = db.Column(db.String(50))
    email = db.Column(db.String(50))
    founded_at = db.Column(db.Date)
    staresina_id = db.Column(db.Integer,db.ForeignKey("users.id"))
    nacelnik_id = db.Column(db.Integer,db.ForeignKey("users.id"))

    staresina = db.relationship('User', foreign_keys=[staresina_id])
    nacelnik = db.relationship('User', foreign_keys=[nacelnik_id])

    members = db.relationship('User', back_populates='odred', foreign_keys=[User.odred_id])

    def __repr__(self):
        return f"<Odred {self.name}>"