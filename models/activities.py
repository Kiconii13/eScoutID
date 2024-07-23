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

    participants = db.relationship('User', secondary='participation', back_populates='activities')

    def __repr__(self):
        return f"<Activity {self.username}>"
