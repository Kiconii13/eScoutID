import os

from flask import Flask
from flask_login import LoginManager
from models import db, User, Odred, Ceta, Vod
from routes import register_blueprints

from config import Config


def create_app(config_class=Config):

    app = Flask(__name__)

    app.config.from_object(config_class)

    db.init_app(app)
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    login_manager = LoginManager()
    login_manager.init_app(app)


    @login_manager.user_loader
    def load_user(user_id):
        return User.query.filter_by(id=user_id).first()


    # Register Blueprints
    register_blueprints(app)

    with app.app_context():
        if not User.query.first():
            db.create_all()

            if len(Odred.query.all()) == 0:
                odred = Odred()
                odred.name = "Genericki odred"
                odred.city = "Genericki grad"
                odred.address = "Genericka adresa"
                odred.nacelnik_id = 1
                odred.staresina_id = 1
                db.session.add(odred)
                db.session.commit()

            if len(Ceta.query.all()) == 0:
                ceta = Ceta()
                ceta.name = "Generička četa"
                ceta.vodja_id = 1
                ceta.odred_id = 1
                db.session.add(ceta)
                db.session.commit()

            if len(Vod.query.all()) == 0:
                vod = Vod()
                vod.name = "Generički vod"
                vod.ceta_id = 1
                vod.vodnik_id = 1
                db.session.add(vod)

            if len(User.query.all()) == 0:
                admin = User(username="savez_admin")
                admin.set_password("")

                admin.odred_id = 1
                admin.vod_id = 1
                admin.role = "savez_admin"

                db.session.add(admin)

                admin = User(username="admin")
                admin.set_password("")

                admin.odred_id = 1
                admin.vod_id = 1
                admin.role = "admin"

                db.session.add(admin)

                db.session.commit()

        return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
