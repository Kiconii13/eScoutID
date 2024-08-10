from functools import wraps

from flask import flash, redirect, url_for
from flask_login import current_user


def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if current_user.role not in roles:
                flash("Nemate dovoljne privilegije za pristup ovoj stranici.", "error")
                return redirect(url_for("dashboard.dashboard"))
            return f(*args, **kwargs)
        return wrapper
    return decorator