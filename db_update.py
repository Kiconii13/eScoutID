from app import db, create_app
from models import User
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

def upgrade():
    try:
        with db.engine.connect() as connection:
            if not hasattr(User, 'jmbg'):
                connection.execute(text('ALTER TABLE users ADD COLUMN jmbg VARCHAR(13);'))
            if not hasattr(User, 'scout_id_number'):
                connection.execute(text('ALTER TABLE users ADD COLUMN scout_id_number VARCHAR(20);'))
            if not hasattr(User, 'account_creation_date'):
                connection.execute(text('ALTER TABLE users ADD COLUMN account_creation_date TIMESTAMP;'))
            if not hasattr(User, 'gender'):
                connection.execute(text('ALTER TABLE users ADD COLUMN gender VARCHAR(10);'))
            if not hasattr(User, 'last_login_date'):
                connection.execute(text('ALTER TABLE users ADD COLUMN last_login_date TIMESTAMP;'))

            connection.execute(text('ALTER TABLE users ALTER COLUMN phone_number TYPE VARCHAR(13);'))

        users = User.query.all()
        for user in users:
            if user.jmbg and not user.gender:
                user.calculate_gender()
                db.session.commit()

        print("Database successfully updated and genders set based on JMBG!")

    except SQLAlchemyError as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        upgrade()