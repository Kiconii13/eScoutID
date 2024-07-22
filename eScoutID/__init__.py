from flask import Flask
app = Flask(__name__)
app.secret_key = "8PvUV36JVw59"

from eScoutID import routes,models