import datetime

from flask import Blueprint, redirect, url_for, render_template, flash, request, make_response, jsonify
from flask_login import login_required, current_user

from models import User, db, Odred, Ceta, Vod, Skill
from permissions import role_required

odred_bp = Blueprint("odred", __name__)


# Prikaz podataka o odredu
@odred_bp.route("/odred")
@login_required
def odred():
    try:
        Broj_Clanova = User.query.filter_by(odred_id=current_user.odred_id).count()
        Broj_clanarina = User.query.filter_by(odred_id=current_user.odred.id, has_paid=True).count()
        return render_template("odred.html", broj_clanova=Broj_Clanova, broj_clanarina=Broj_clanarina)
    except:
        flash("Morate biti član odreda!", "Greška")
        return redirect(url_for("dashboard.dashboard"))


# Prikaz tabele sa svim clanovima; Prikazuju se samo clanovi odreda ciji je admin trenutno ulogovani korisnik.
@odred_bp.route("/odredDashboard/<int:id>")
@login_required
@role_required("admin", "savez_admin")
def odredDashboard(id):
    if current_user.odred.id != id and current_user.role != "savez_admin":
        return redirect(url_for("odred.odred"))
    cetas = Ceta.query.filter_by(odred_id=current_user.odred_id).all()
    ceta_ids = [ceta.id for ceta in cetas]
    vods = Vod.query.filter(Vod.ceta_id.in_(ceta_ids)).order_by(Vod.ceta_id).all()
    now = datetime.date.today()
    return render_template("OdredDashboard.html", odred_name=Odred.query.filter_by(id=id).first(),
                           users=User.query.filter_by(odred_id=id).order_by(User.id).all(), vods=vods, now = now)


# Dodavanje novog clana u odred
@odred_bp.route("/clan/add", methods=["POST", "GET"])
@login_required
@role_required("admin", "savez_admin")
def addClan():
    action = "add"
    new_user = User()
    if request.method == "POST":
        if request.form["role"] == "savez_admin" and current_user.role != "savez_admin":
            flash("Nedozvoljena radnja!", "Greška")
            return redirect(url_for("dashboard.dashboard"))
        if request.form["role"] not in ["clan", "admin", "savez_admin"]:
            flash("Nedozvoljena radnja!", "Greška")
            return redirect(url_for("dashboard.dashboard"))
        new_user = User.defUser(new_user)
        new_user.set_password(new_user.username)
        db.session.add(new_user)
        db.session.commit()
        new_user.username = f"{new_user.username}{new_user.id}c"
        new_user.set_password(new_user.username)
        new_user.odred_id = current_user.odred_id
        db.session.commit()
        return redirect(url_for("odred.odredDashboard", id=current_user.odred.id))
    else:
        cetas = Ceta.query.filter_by(odred_id=current_user.odred_id).all()
        ceta_ids = [ceta.id for ceta in cetas]
        vods = Vod.query.filter(Vod.ceta_id.in_(ceta_ids)).all()
        return render_template("addClan.html", h1="Dodaj člana", action=action, clan=new_user, vods=vods)


# Izmene podataka vec postojeceg clana odreda
@odred_bp.route("/clan/edit/<int:id>", methods=["POST", "GET"])
@login_required
@role_required("admin", "savez_admin")
def editClan(id):
    action = "edit"
    user = User.query.get(id)
    if user.odred.id != current_user.odred.id and current_user.role != "savez_admin":
        return redirect(url_for("odred.odred"))
    cetas = Ceta.query.filter_by(odred_id=user.odred_id).all()
    ceta_ids = [ceta.id for ceta in cetas]
    vods = Vod.query.filter(Vod.ceta_id.in_(ceta_ids)).all()
    if request.method == "POST":
        if user.vod.vodnik_id == user.id and user.vod.id != int(request.form["vod"]):
            flash("Clan je vodnik svog voda! Prvo postavi drugog vodnika.", "Greška")
            return render_template("addClan.html", h1="Izmeni člana", action=action, clan=user,
                                   odred=Odred.query.filter_by(id=user.odred_id).first().name, vods=vods)
        if (request.form["role"] == "savez_admin" and current_user.role != "savez_admin") or (
                request.form["role"] not in ["clan", "admin", "savez_admin"]):
            flash("Nedozvoljena radnja!", "Greška")
            return redirect(url_for("dashboard.dashboard"))
        user = User.defUser(user)
        db.session.commit()
        return redirect(url_for("odred.odredDashboard", id=user.odred.id))
    else:
        return render_template("addClan.html", h1="Izmeni člana", action=action, clan=user,
                               odred=Odred.query.filter_by(id=user.odred_id).first().name, vods=vods)


# Uklanjanje clana iz odreda
@odred_bp.route("/clan/delete/<int:id>", methods=["GET", "POST"])
@login_required
@role_required("admin", "savez_admin")
def deleteClan(id):
    user = User.query.get(id)
    if user:
        if user.id not in [user.odred.staresina_id, user.odred.nacelnik_id, user.vod.vodnik_id, user.vod.ceta.vodja_id]:
            if user.odred.id != current_user.odred.id and current_user.role != "savez_admin":
                return redirect(url_for("odred.odred"))
            db.session.delete(user)
            db.session.commit()
            flash("Član je uspešno obrisan.", "Info")
        else:
            flash("Član vrši dužnost u odredu! Možeš obrisati samo članove koji su razrešeni dužnosti", "Greška")
    else:
        flash("Član nije pronađen.", "Greška")
    return redirect(url_for("odred.odredDashboard", id=current_user.odred.id))


# Pretraga avatara korisnika
@odred_bp.route("/clan/avatar/<int:id>")
@login_required
def getPfp(id):
    user = User.query.filter_by(id=id).first()
    if user.avatar:
        response = make_response(user.avatar, 200)
    else:
        response = make_response("default", 200)
    response.mimetype = "text/plain"
    return response


@odred_bp.route("/clan/avatar/update/<int:id>", methods=['POST'])
@login_required
def updatePfp(id):
    user = User.query.get_or_404(id)
    if user.id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403

    data = request.get_json()
    if data['image'] != "nochange":
        user.avatar = data['image']
        db.session.commit()
        return jsonify({"success": True}), 200
    else:
        return jsonify({"error": "No image provided"}), 400


@odred_bp.route("/cv/add", methods=["GET", "POST"])
@login_required
@role_required("admin")
def addCetaVod():
    return render_template("addCetaVod.html", users=User.query.filter_by(odred_id=current_user.odred_id).order_by(User.id).all(), cetas=Ceta.query.filter_by(odred_id=current_user.odred_id).order_by(Ceta.id).all())


@odred_bp.route("/ceta/new", methods=["POST"])
@login_required
@role_required("admin")
def newCeta():
    ceta = Ceta()

    ceta.name = request.form["name"]
    cete = Ceta.query.filter_by(odred_id=current_user.odred.id).all()
    if any(existing_ceta.name == ceta.name for existing_ceta in cete):
        flash("Četa sa tim imenom već postoji u odredu!", "Greška")
        return redirect(url_for("odred.addCetaVod"))
    ceta.odred_id = current_user.odred.id
    db.session.add(ceta)
    db.session.commit()

    flash("Četa uspešno dodata!", "Info")
    return redirect(url_for("odred.addCetaVod"))


@odred_bp.route("/vod/new", methods=["POST"])
@login_required
@role_required("admin")
def newVod():
    vod = Vod()

    vod.name = request.form["name"]
    vod.vodnik_id = request.form["vodnik"]
    vod.ceta_id = request.form["ceta"]

    db.session.add(vod)
    db.session.commit()

    vod.vodnik.vod_id = vod.id
    db.session.commit()

    flash("Vod uspešno dodat!", "Info")
    return redirect(url_for("odred.addCetaVod"))


@odred_bp.route("/edit/roles")
@login_required
@role_required("admin")
def editRoles():
    cetas = Ceta.query.filter_by(odred_id=current_user.odred_id).all()
    ceta_ids = [ceta.id for ceta in cetas]
    vods = Vod.query.filter(Vod.ceta_id.in_(ceta_ids)).all()
    users = User.query.filter_by(odred_id=current_user.odred_id).order_by(User.dob.asc()).all()

    return render_template("editRoles.html", vods=vods, users=users, cetas=cetas,
                           current_staresina=current_user.odred.staresina.id,
                           current_nacelnik=current_user.odred.nacelnik.id)


@odred_bp.route("/edit/roles/vodnik", methods=["POST"])
@login_required
@role_required("admin")
def editVodnik():
    vod = Vod.query.filter_by(id=request.form["vod"]).first()

    vod.vodnik_id = request.form["vodnik"]

    db.session.commit()

    flash("Novi vodnik postavljen", "Info")
    return redirect(url_for("odred.editRoles"))


@odred_bp.route("/edit/roles/vodjacete", methods=["POST"])
@login_required
@role_required("admin")
def editVodjacete():
    ceta = Ceta.query.filter_by(id=request.form["ceta"]).first()

    ceta.vodja_id = request.form["vodjacete"]

    db.session.commit()

    flash("Novi vođa čete postavljen", "Info")
    return redirect(url_for("odred.editRoles"))


@odred_bp.route("/edit/nacelnik", methods=["POST"])
@login_required
@role_required("admin")
def editNacelnikStaresina():
    current_user.odred.staresina_id = request.form["staresina"]
    current_user.odred.nacelnik_id = request.form["nacelnik"]

    db.session.commit()

    flash("Načelnik i starešina uspešno ažurirani", "Info")
    return redirect(url_for("odred.editRoles"))


@odred_bp.route("/vodInfo/<int:id>")
@login_required
def vodInfo(id):
    if current_user.role == "clan" and current_user.vod.id != id:
        return redirect(url_for("dashboard.dashboard"))
    return render_template("editVod.html", vod=Vod.query.get(id),
                           users=User.query.filter_by(vod_id=id).all(),
                           cete=Ceta.query.filter_by(odred_id=current_user.odred.id).all())


@odred_bp.route("/editVod/<int:id>", methods=["POST"])
@login_required
@role_required("admin")
def editVod(id):
    vod = Vod.query.get(id)
    if vod.ceta.odred_id != current_user.odred_id:
        return redirect(url_for("odred.odred"))
    vod.name = request.form.get("vod_name")
    vod.ceta_id = request.form.get("ceta")
    db.session.commit()
    return redirect(url_for("odred.vodInfo", id=id))


@odred_bp.route("/deleteVod/<int:id>")
@login_required
@role_required("admin")
def deleteVod(id):
    if len(User.query.filter_by(vod_id=id).all()) == 0:
        vod = Vod.query.get(id)
        if vod.ceta.odred_id != current_user.odred_id:
            return redirect(url_for("odred.odred"))
        db.session.delete(vod)
        db.session.commit()
        flash("Vod je uspešno obrisan", "Info")
        return redirect(url_for("odred.odredDashboard", id=current_user.odred_id))
    else:
        flash("Vod ne sme imati članove koji mu pripadaju ukoliko želite da ga obrišete", "Greška")
        return redirect(url_for("odred.vodInfo", id=id))
