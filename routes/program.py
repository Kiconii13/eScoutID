from datetime import datetime

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from models import User, db, Skill
from permissions import role_required

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
@role_required("admin")
def add_program():
    users, selected_user, skills = get_users_and_selected_user()
    return render_template('addProgram.html', users=users, selected_user=selected_user, skills=skills)


# Ruta za prikaz člana izabranog u select-u
@program_bp.route('/select_user', methods=['POST'])
@login_required
@role_required("admin")
def select_user():
    user_id = request.form['user']
    users, selected_user, skills = get_users_and_selected_user(user_id)
    return render_template('addProgram.html', users=users, selected_user=selected_user, skills=skills)


# Prikupljaju se rednosti upisane u formi za nivoe položenog programa člana
# Prikupljaju se trenutne informacije o nivoima položenog programa za odabranog člana
# Unose se izmene i osvežava se stranica
@program_bp.route('/update_levels', methods=['POST'])
@login_required
@role_required("admin")
def update_levels():
    user_id = request.form['user']
    let_level = request.form['let_level']
    zvezda_level = request.form['zvezda_level']
    krin_level = request.form['krin_level']

    selected_user = User.query.get(user_id)
    selected_user.let_level = let_level
    selected_user.zvezda_level = zvezda_level
    selected_user.krin_level = krin_level
    db.session.commit()

    return redirect(url_for('program.add_program'))


# Sličan princip kao za rutu iznad
@program_bp.route('/add_skill', methods=['POST'])
@login_required
@role_required("admin")
def add_skill():
    user_id = request.form['user_id']
    name = request.form['name']
    level = request.form['level']
    date_got = datetime.strptime(request.form['date_got'], '%Y-%m-%d')

    new_skill = Skill(user_id=user_id, name=name, level=level, date_got=date_got)
    db.session.add(new_skill)
    db.session.commit()

    return redirect(url_for('program.add_program', user_id=user_id))


@program_bp.route('/delete_skill/<int:id>', methods=['POST', 'GET'])
@login_required
@role_required("admin")
def delete_skill(id):
    skill = Skill.query.get(id)
    user_id = skill.user_id
    user = User.query.get(user_id)
    if user.odred.id != current_user.odred.id:
        return redirect(url_for("odred.odred"))
    db.session.delete(skill)
    db.session.commit()
    flash("Uspešno obrisan posebni program", "info")
    return redirect(url_for('program.add_program', user_id=user_id))
