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

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
