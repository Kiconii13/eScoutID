from sqlite3 import Date

from . import db


class Skill(db.Model):
    __tablename__ = "skills"
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey("users.id", ondelete="CASCADE"))
    name = db.Column(db.String())
    level = db.Column(db.Integer())
    date_got = db.Column(db.Date(), default=Date.today())

    user = db.relationship("User", back_populates="skills")
