from datetime import datetime

from flask import Blueprint, render_template, request
from flask_login import login_required, current_user

from models import User, db, Skill

program_bp = Blueprint('program', __name__)


@program_bp.route("/program")
@login_required
def program():
    skills = Skill.query.filter_by(user_id=current_user.id).all()
    return render_template("program.html", skills=skills)


@program_bp.route('/addProgram', methods=['GET', 'POST'])
@login_required
def addProgram():
    users = User.query.filter_by(odred_id=current_user.odred.id)
    selected_user = None
    skills = []

    if request.method == 'POST':
        if 'update_levels' in request.form:
            user_id = request.form['user']
            let_level = request.form['let_level']
            zvezda_level = request.form['zvezda_level']
            krin_level = request.form['krin_level']

            selected_user = User.query.get(user_id)
            selected_user.let_level = let_level
            selected_user.zvezda_level = zvezda_level
            selected_user.krin_level = krin_level
            db.session.commit()
        elif 'select_user' in request.form:
            user_id = request.form['user']
            selected_user = User.query.get(user_id)
            skills = Skill.query.filter_by(user_id=user_id).all()
        elif 'add_skill' in request.form:
            user_id = request.form['user_id']
            name = request.form['name']
            level = request.form['level']
            date_got = datetime.strptime(request.form['date_got'], '%Y-%m-%d')

            new_skill = Skill(user_id=user_id, name=name, level=level, date_got=date_got)
            db.session.add(new_skill)
            db.session.commit()

            selected_user = User.query.get(user_id)
            skills = Skill.query.filter_by(user_id=user_id).all()

    if not selected_user and users:
        selected_user = users[0]
        skills = Skill.query.filter_by(user_id=selected_user.id).all()

    return render_template('addProgram.html', users=users, selected_user=selected_user, skills=skills)
