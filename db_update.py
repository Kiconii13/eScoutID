from app import db, create_app
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

def upgrade():
    try:
        with db.engine.connect() as connection:
            # Dodajte kolone ako ne postoje
            connection.execute(text('ALTER TABLE activity ADD COLUMN IF NOT EXISTS key VARCHAR(50);'))

        print("Database successfully updated!")

    except SQLAlchemyError as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        upgrade()