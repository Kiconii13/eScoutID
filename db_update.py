from app import db, create_app
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

def upgrade():
    try:
        with db.engine.connect() as connection:
            # Proverite da li kolone postoje pre nego što ih dodate
            result = connection.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'users'
            """))
            existing_columns = {row['column_name'] for row in result}

            if 'jmbg' not in existing_columns:
                connection.execute(text('ALTER TABLE users ADD COLUMN jmbg VARCHAR(13);'))
            if 'scout_id_number' not in existing_columns:
                connection.execute(text('ALTER TABLE users ADD COLUMN scout_id_number VARCHAR(20);'))
            if 'account_creation_date' not in existing_columns:
                connection.execute(text('ALTER TABLE users ADD COLUMN account_creation_date TIMESTAMP;'))
            if 'gender' not in existing_columns:
                connection.execute(text('ALTER TABLE users ADD COLUMN gender VARCHAR(10);'))
            if 'last_login_date' not in existing_columns:
                connection.execute(text('ALTER TABLE users ADD COLUMN last_login_date TIMESTAMP;'))

            # Promenite tip kolone ako je potrebno
            connection.execute(text('ALTER TABLE users ALTER COLUMN phone_number TYPE VARCHAR(13);'))

        # Postavite polje 'gender' na osnovu 'jmbg' za sve postojeće korisnike
        from models import User
        users = User.query.all()
        for user in users:
            if user.jmbg and not user.gender:
                user.calculate_gender()  # Pretpostavljam da imate ovu metodu u modelu User
                db.session.commit()

        print("Database successfully updated and genders set based on JMBG!")

    except SQLAlchemyError as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        upgrade()
