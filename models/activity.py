from . import db
from sqlalchemy import Enum
import enum


class ActivityType(enum.Enum):
    Aktivnost = 1
    Tecaj = 2
    Seminar = 3
    Izlet = 4
    Bivak = 5
    Tabor = 6
    Smotra = 7

    def __str__(self):
        return self.name


class OrganizerLevel(enum.Enum):
    Odred = 1
    Savez = 2
    International = 3


class Activity(db.Model):
    __tablename__ = "activities"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    due_date = db.Column(db.Date)
    location = db.Column(db.String(50))
    type = db.Column(Enum(ActivityType), default=ActivityType.Aktivnost)
    organizer_type = db.Column(Enum(OrganizerLevel), default=OrganizerLevel.Odred)
    organizer_name = db.Column(db.String(50))

    participants = db.relationship('User', secondary='participations', back_populates='activities')

    def __repr__(self):
        return f"<Activity {self.id}>"


class Participation(db.Model):
    __tablename__ = "participations"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"))
    activity_id = db.Column(db.Integer, db.ForeignKey("activities.id", ondelete="CASCADE"))

    def __repr__(self):
        return f"<Participation {self.id}>"
