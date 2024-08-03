import os


class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get("NEW_DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get("SECRET_KEY")
    UPLOAD_FOLDER = "uploads/"