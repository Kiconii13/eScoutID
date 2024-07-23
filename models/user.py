from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


class User(db.Model, UserMixin):
    __tablename__ = "users"

    # Class Variables
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), unique=True, nullable=False)
    password_hash = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(16), default="clan")
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    dob = db.Column(db.String(12))
    join_date = db.Column(db.String(12))
    phone_number = db.Column(db.String(12))
    email = db.Column(db.String(100))
    address = db.Column(db.String(100))
    has_paid = db.Column(db.Boolean(), default=False)
    jedinica = db.Column(db.String(30))
    
    odred_id = db.Column(db.Integer,db.ForeignKey("odred.id"))

    odred = db.relationship('Odred', back_populates='members', foreign_keys=[odred_id])
    activities = db.relationship('Activity', secondary='participation', back_populates='participants')


    def set_password(self, password):
        self.password_hash = generate_password_hash(password)


    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    

    def get_id(self):
        return str(self.id)
    
    @property
    def is_active(self):
        # Optional: Implement if you have an activation process for users
        return True

    @property
    def is_authenticated(self):
        return True  # Assuming all users are authenticated

    @property
    def is_anonymous(self):
        return False

    @staticmethod
    def get(user_id):
        return User.query.get(int(user_id))

    def __repr__(self):
        return f"<User {self.username}>"