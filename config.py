import os

class Config:
    if os.environ.get("FLASK_ENV") == "development":
        SQLALCHEMY_DATABASE_URI = "sqlite:///eScoutID.db"
        SECRET_KEY = os.environ.get("8PvUV36JVw59")
    else:
        SQLALCHEMY_DATABASE_URI = os.environ.get("NEW_DATABASE_URL")
        SECRET_KEY = os.environ.get("SECRET_KEY")

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = "uploads/"
