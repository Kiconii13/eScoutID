from . import db, User, Activity


class Participation(db.Model):
    __tablename__ = "participations"

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    activity_id = db.Column(db.Integer, db.ForeignKey("activities.id"), primary_key=True)

    user = db.relationship('User', backref='participations')
    activity = db.relationship('Activity', backref='participations')

    def __repr__(self):
        return f"<Participation {self.username}>"
