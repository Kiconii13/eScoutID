from flask import Flask
from flask_login import LoginManager
from models import db, User, Odred
from routes import register_blueprints

from config import Config


def create_app(config_class=Config):

    app = Flask(__name__)

    app.config.from_object(config_class)

    # app.secret_key = "8PvUV36JVw59"

    # Configure SQL Alchemy
    # app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///eScoutID.db"
    # app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.init_app(app)


    @login_manager.user_loader
    def load_user(user_id):
        return User.query.filter_by(id=user_id).first()


    # Register Blueprints
    register_blueprints(app)

    with app.app_context():
        db.create_all()

        if len(Odred.query.all()) == 0:
            odred = Odred()
            odred.name = "Genericki odred"
            odred.city = "Genericki grad"
            odred.address = "Genericka adresa"
            db.session.add(odred)
            db.session.commit()

        if len(User.query.all()) == 0:
            admin = User(username="admin")
            admin.set_password("")

            admin.odred_id = 1
            admin.role = "admin"

            db.session.add(admin)
            db.session.commit()

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
