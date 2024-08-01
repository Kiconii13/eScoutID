import os
from app import create_app

# Set up the Flask application
app = create_app()

if __name__ == "__main__":
    app.run()
