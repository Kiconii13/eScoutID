from datetime import datetime

from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user

from models import User, db, Skill

program_bp = Blueprint('program', __name__)


# Ispis položenog programa trenutnog člana
# Skills se odnosi na veštine, veštarstva i specijalnosti
# Podaci o letovima, zvezdama i krinovima se čuvaju u tabeli user po nivoima (od 0 do 3)
@program_bp.route("/program")
@login_required
def program():
    skills = Skill.query.filter_by(user_id=current_user.id).all()
    return render_template("program.html", skills=skills)


# Pomoćna funkcija za prikupljanje informacija za prikaz stranice za upravljanje programom
def get_users_and_selected_user(user_id=None):
    users = User.query.filter_by(odred_id=current_user.odred.id).all()
    selected_user = User.query.get(user_id) if user_id else (users[0] if users else None)
    skills = Skill.query.filter_by(user_id=selected_user.id).all() if selected_user else []
    return users, selected_user, skills


# Priakaz stranice
@program_bp.route('/addProgram', methods=['GET'])
@login_required
def add_program():
    users, selected_user, skills = get_users_and_selected_user()
    return render_template('addProgram.html', users=users, selected_user=selected_user, skills=skills)


# Ruta za prikaz člana izabranog u select-u
@program_bp.route('/select_user', methods=['POST'])
@login_required
def select_user():
    user_id = request.form['user']
    users, selected_user, skills = get_users_and_selected_user(user_id)
    return render_template('addProgram.html', users=users, selected_user=selected_user, skills=skills)


@program_bp.route('/update_levels', methods=['POST'])
@login_required
def update_levels():
    # Prikupljaju se vrednosti upisane u formi za nivoe položenog programa člana
    user_id = request.form['user']
    let_level = request.form['let_level']
    zvezda_level = request.form['zvezda_level']
    krin_level = request.form['krin_level']

    # Ažuriraju se trenutne informacije o nivoima položenog programa za odabranog člana
    selected_user = User.query.get(user_id)
    selected_user.let_level = let_level
    selected_user.zvezda_level = zvezda_level
    selected_user.krin_level = krin_level

    # Unose se izmene i osvežava se stranica
    db.session.commit()

    current_app.logger.log(25, f"Korisnik {current_user.first_name} {current_user.last_name} (id: {current_user.id}) ažurirao je podatke o nivoima člana {selected_user.first_name} {selected_user.last_name} (id: {selected_user.id})")
    return redirect(url_for('program.add_program'))


# Sličan princip kao za rutu iznad
@program_bp.route('/add_skill', methods=['POST'])
@login_required
def add_skill():
    user_id = request.form['user_id']

    user = User.query.get(user_id)

    name = request.form['name']
    level = request.form['level']
    date_got = datetime.strptime(request.form['date_got'], '%Y-%m-%d')

    new_skill = Skill(user_id=user_id, name=name, level=level, date_got=date_got)
    
    db.session.add(new_skill)
    db.session.commit()

    current_app.logger.log(25, f"Korisnik {current_user.first_name} {current_user.last_name} (id: {current_user.id}) zabeležio je novu veštinu {new_skill.name} {new_skill.level} za korisnika {user.first_name} {user.last_name} (id: {user.id})")
    return redirect(url_for('program.add_program', user_id=user_id))

@program_bp.route('/delete_skill/<int:id>', methods=['POST', 'GET'])
@login_required
def delete_skill(id):
    if current_user.role == "admin":
        return redirect(url_for("dashboard.dashboard"))
    
    skill = Skill.query.get(id)

    sn = f"{skill.name} {skill.level}"

    user_id = skill.user_id

    db.session.delete(skill)
    db.session.commit()

    user = User.query.get(user_id)

    flash("Uspešno obrisan posebni program", "info")
    current_app.logger.log(25, f"Korisnik {current_user.first_name} {current_user.last_name} (id: {current_user.id}) obrisao je veštinu {sn} korisnika {user.first_name} {user.last_name} (id: {user.id})")
    return redirect(url_for('program.add_program', user_id=user_id))