from eScoutID import app
from flask_sqlalchemy import SQLAlchemy
import sqlitecloud
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///eScoutID.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


class User:
    def __init__(self, id, username, password_hash, role, first_name, last_name, odred_id, birth_date, mobile_number,
                 home_address, email, membership_fee):
        self.id = id
        self.username = username
        self.password_hash = password_hash
        self.role = role
        self.first_name = first_name
        self.last_name = last_name
        self.odred_id = odred_id
        self.birth_date = birth_date
        self.mobile_number = mobile_number
        self.home_address = home_address
        self.email = email
        self.membership_fee = membership_fee

    @classmethod
    def from_row(cls, row):
        return cls(
            id=int(row[0]) if row[0] is not None else None,
            username=str(row[1]) if row[1] is not None else None,
            password_hash=str(row[2]) if row[2] is not None else None,
            role=str(row[3]) if row[3] is not None else 'clan',
            first_name=str(row[4]) if row[4] is not None else None,
            last_name=str(row[5]) if row[5] is not None else None,
            odred_id=int(row[6]) if row[6] is not None else None,
            birth_date=datetime.strptime(row[7], '%Y-%m-%d') if row[7] is not None else None,
            mobile_number=str(row[8]) if row[8] is not None else None,
            home_address=str(row[9]) if row[9] is not None else None,
            email=str(row[10]) if row[10] is not None else None,
            membership_fee=bool(row[11]) if row[11] is not None else False
        )

    @classmethod
    def username_only(cls, username):
        return cls(
            id=None,
            username=username,
            password_hash=None,
            role=None,
            first_name=None,
            last_name=None,
            odred_id=1,
            birth_date=None,
            mobile_number=None,
            home_address=None,
            email=None,
            membership_fee=False
        )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Odred(db.Model):
    # Class Variables
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    city = db.Column(db.String(50))
    address = db.Column(db.String(50))
    email = db.Column(db.String(50))
    founded_at = db.Column(db.Date)
    staresina_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    nacelnik_id = db.Column(db.Integer, db.ForeignKey("user.id"))


def get_by_username(username):
    conn = sqlitecloud.connect(
        'sqlitecloud://cr94e8txiz.sqlite.cloud:8860?apikey=jdf7bvL8D9DUR6Nu7KbSrkobWvovpjhV0SO3qTnfzbE')

    db_name = 'eScoutID.db'
    db_query = f"SELECT * FROM USER WHERE user.username = '{username}'"

    conn.execute(f"USE DATABASE {db_name}")

    cursor = conn.execute(db_query)

    conn.close()
    user = None
    for row in cursor:
        user = User.from_row(row)

    return user


def add_new_user(username, password_hash):
    conn = sqlitecloud.connect(
        'sqlitecloud://cr94e8txiz.sqlite.cloud:8860?apikey=jdf7bvL8D9DUR6Nu7KbSrkobWvovpjhV0SO3qTnfzbE')

    db_name = 'eScoutID.db'
    db_query = f"INSERT INTO USER(username, password_hash) values ('{username}','{password_hash}')"

    conn.execute(f"USE DATABASE {db_name}")

    conn.execute(db_query)

    conn.commit()

    conn.close()


def edit_name(name, username):
    conn = sqlitecloud.connect(
        'sqlitecloud://cr94e8txiz.sqlite.cloud:8860?apikey=jdf7bvL8D9DUR6Nu7KbSrkobWvovpjhV0SO3qTnfzbE')

    db_name = 'eScoutID.db'
    db_query = f"UPDATE USER SET first_name='{name}' WHERE username='{username}'"

    conn.execute(f"USE DATABASE {db_name}")

    conn.execute(db_query)

    conn.close()


def get_users(odred_id):
    conn = sqlitecloud.connect(
        'sqlitecloud://cr94e8txiz.sqlite.cloud:8860?apikey=jdf7bvL8D9DUR6Nu7KbSrkobWvovpjhV0SO3qTnfzbE')

    db_name = 'eScoutID.db'
    db_query = f"SELECT * FROM USER WHERE user.odred_id='{odred_id}'"

    conn.execute(f"USE DATABASE {db_name}")

    cursor = conn.execute(db_query)

    conn.close()
    clanovi = []
    for row in cursor:
        user = User.from_row(row)
        clanovi.append(user)

    return clanovi
