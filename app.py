import os
import logging
from datetime import datetime

from flask import Flask, redirect, url_for
# from flask_migrate import Migrate
from flask_login import LoginManager
from models import db, User, Odred, Ceta, Vod
from routes import register_blueprints

from config import Config


def create_app(config_class=Config):
    # logger = logging.getLogger(__name__)
    
    if not os.path.exists("logs/"):
        os.mkdir("logs/")
    

    fileNameString = f"{Config.LOG_BASE_PATH}/{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.log"

    # logging.basicConfig(filename=fileNameString, level=logging.INFO)

    app = Flask(__name__)

    app.config.from_object(config_class)

    app.logger.setLevel(logging.INFO)
    handler = logging.FileHandler(fileNameString)
    handler.setFormatter(logging.Formatter(f'%(asctime)s|%(levelname)s|%(name)s|msg=%(message)s'))
    # TODO: napraviti i handlera za mejl
    #       ref: https://flask.palletsprojects.com/en/2.3.x/logging/#email-errors-to-admins
    app.logger.addHandler(handler)

    db.init_app(app)
    # migrate = Migrate(app, db)

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    login_manager = LoginManager()
    login_manager.init_app(app)


    @login_manager.user_loader
    def load_user(user_id):
        return User.query.filter_by(id=user_id).first()

    @login_manager.unauthorized_handler
    def unauthorized():
        return redirect(url_for('auth.index'))  # Naziv view funkcije za login stranicu


    # Register Blueprints
    register_blueprints(app)

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
