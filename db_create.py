from app import db
from app import create_app
from models import User, Odred, Ceta, Vod

app = create_app()

with app.app_context():
    db.create_all()
    if not User.query.first():
        odred = Odred()
        odred.name = "Genericki odred"
        odred.city = "Genericki grad"
        odred.address = "Genericka adresa"

        db.session.add(odred)

        ceta = Ceta()
        ceta.name = "Generička četa"

        db.session.add(ceta)

        vod = Vod()
        vod.name = "Generički vod"

        db.session.add(vod)

        savez_admin = User(username="savez_admin")
        savez_admin.set_password("")
        savez_admin.role = "savez_admin"
        savez_admin.odred_id = odred.id
        savez_admin.vod_id = vod.id

        db.session.add(savez_admin)

        admin = User(username="admin")
        admin.set_password("")
        admin.role = "admin"

        db.session.add(admin)
        db.session.commit()

    admin_user = User.query.filter_by(role="admin").first()
    if not admin_user.odred_id:
        admin_user.odred_id = Odred.query.first().id
        admin_user.vod_id = Vod.query.first().id

        db.session.commit()

    savez_admin_user = User.query.filter_by(role="admin").first()
    if not savez_admin_user.odred_id:
        savez_admin_user.odred_id = Odred.query.first().id
        savez_admin_user.vod_id = Vod.query.first().id

        db.session.commit()

    vod = Vod.query.first()
    if not vod.ceta_id:
        vod.ceta_id = Ceta.query.first().id
        vod.vodnik_id = User.query.first().id

        db.session.commit()

    ceta = Ceta.query.first()
    if not ceta.vodja_id:
        ceta.vodja_id = User.query.first().id
        ceta.odred_id = Odred.query.first().id

        db.session.commit()

    odred = Odred.query.first()
    if not odred.nacelnik_id:
        odred.nacelnik_id = User.query.first().id
        odred.staresina_id = User.query.first().id

        db.session.commit()