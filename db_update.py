from app import db, create_app
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

def upgrade():
    try:
        # Pokrećemo novu transakciju
        with db.session.begin():
            # Dodajte kolonu ako ne postoji
            db.session.execute(text('ALTER TABLE activities ADD COLUMN IF NOT EXISTS key VARCHAR(50);'))

        db.session.commit()  # Obavezno sačuvaj promene
        print("Database successfully updated!")

    except SQLAlchemyError as e:
        db.session.rollback()  # Ako dođe do greške, vrati sve promene unazad
        print(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        upgrade()
