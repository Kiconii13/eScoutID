from .auth import auth_bp
from .dashboard import dashboard_bp
from .savez import savez_bp
from .aktivnosti import aktivnosti_bp
from .program import program_bp
from .odred import odred_bp


def register_blueprints(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(savez_bp)
    app.register_blueprint(aktivnosti_bp)
    app.register_blueprint(program_bp)
    app.register_blueprint(odred_bp)
