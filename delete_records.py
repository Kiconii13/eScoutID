from app import db, create_app
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError


def clear_activities():
    try:
        # Pokrećemo novu transakciju
        with db.session.begin():
            # Brisanje svih podataka iz tabele activities
            db.session.execute(text('DELETE FROM activities;'))

        db.session.commit()  # Obavezno sačuvaj promene
        print("All records from 'activities' table have been successfully deleted!")

    except SQLAlchemyError as e:
        db.session.rollback()  # Ako dođe do greške, vrati sve promene unazad
        print(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        clear_activities()
