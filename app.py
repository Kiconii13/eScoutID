import os

from flask import Flask
# from flask_migrate import Migrate
from flask_login import LoginManager
from models import db, User, Odred, Ceta, Vod
from routes import register_blueprints

from config import Config


def create_app(config_class=Config):
    app = Flask(__name__)

    app.config.from_object(config_class)

    db.init_app(app)
    # migrate = Migrate(app, db)

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    login_manager = LoginManager()
    login_manager.init_app(app)


    @login_manager.user_loader
    def load_user(user_id):
        return User.query.filter_by(id=user_id).first()


    # Register Blueprints
    register_blueprints(app)

    with app.app_context():
        db.create_all()
        if not User.query.first():
            odred = Odred()
            odred.name = "Genericki odred"
            odred.city = "Genericki grad"
            odred.address = "Genericka adresa"
            
            db.session.add(odred)
            
            ceta = Ceta()
            ceta.name = "Generička četa"
            
            db.session.add(ceta)

            vod = Vod()
            vod.name = "Generički vod"
            
            db.session.add(vod)

            savez_admin = User(username="savez_admin")
            savez_admin.set_password("")
            savez_admin.role = "savez_admin"
            savez_admin.odred_id = odred.id
            savez_admin.vod_id = vod.id

            db.session.add(savez_admin)

            admin = User(username="admin")
            admin.set_password("")
            admin.role = "admin"

            db.session.add(admin)

            odred.nacelnik_id = admin.id
            odred.staresina_id = admin.id
            ceta.vodja_id = admin.id
            ceta.odred_id = odred.id
            vod.ceta_id = ceta.id
            vod.vodnik_id = admin.id
            admin.odred_id = odred.id
            admin.vod_id = vod.id

            db.session.commit()

        return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
