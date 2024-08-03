import os
class Config:
    # SQLALCHEMY_DATABASE_URI = os.environ.get("NEW_DATABASE_URL")
    SQLALCHEMY_DATABASE_URI = "postgresql://u3u1ajj9ent4i7:p1c6601288bee675465b17d846d93aa045705c1551f41c7f5b1ae5642a6459f0a@cah8ha8ra8h8i7.cluster-czz5s0kz4scl.eu-west-1.rds.amazonaws.com:5432/db6q0misa71vdf"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # SECRET_KEY = os.environ.get("SECRET_KEY")
    SECRET_KEY = "8PvUV36JVw59"
    UPLOAD_FOLDER = "uploads/"