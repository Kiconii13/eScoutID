from flask_sqlalchemy import SQLAlchemy

# Initialize SQLAlchemy instance
db = SQLAlchemy()

# Import models
from .user import User
from .odred import Odred
from .skill import Skill
