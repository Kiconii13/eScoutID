from app import db
from app import app

app.app_context().push()
db.create_all()