from app import db, create_app
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

def upgrade():
    try:
        with db.engine.connect() as connection:
            # Dodajte kolone ako ne postoje
            connection.execute(text('ALTER TABLE users ADD COLUMN IF NOT EXISTS jmbg VARCHAR(13);'))
            connection.execute(text('ALTER TABLE users ADD COLUMN IF NOT EXISTS scout_id_number VARCHAR(20);'))
            connection.execute(text('ALTER TABLE users ADD COLUMN IF NOT EXISTS account_creation_date TIMESTAMP;'))
            connection.execute(text('ALTER TABLE users ADD COLUMN IF NOT EXISTS gender VARCHAR(10);'))
            connection.execute(text('ALTER TABLE users ADD COLUMN IF NOT EXISTS last_login_date TIMESTAMP;'))

            # Promenite tip kolone ako je potrebno
            connection.execute(text('ALTER TABLE users ALTER COLUMN phone_number TYPE VARCHAR(13);'))

        print("Database successfully updated!")

    except SQLAlchemyError as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        upgrade()