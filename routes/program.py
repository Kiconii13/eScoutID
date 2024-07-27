from datetime import datetime

from flask import Blueprint, flash, render_template, request, redirect, url_for, jsonify
from flask_login import login_required, current_user

from models import User, db, Skill

program_bp = Blueprint('program', __name__)


@program_bp.route("/program")
@login_required
def program():
    return render_template("program.html")


@program_bp.route('/addProgram', methods=['GET', 'POST'])
@login_required
def addProgram():
    users = User.query.filter_by(odred_id = current_user.odred.id)
    if request.method == 'POST':
        user_id = request.form['user']
        let_level = request.form['let_level']
        zvezda_level = request.form['zvezda_level']
        krin_level = request.form['krin_level']

        user = User.query.get(user_id)
        user.let_level = let_level
        user.zvezda_level = zvezda_level
        user.krin_level = krin_level
        db.session.commit()

        return redirect(url_for('program.addProgram'))

    return render_template('addProgram.html', users=users)

@program_bp.route('/get_user_levels/<int:user_id>')
@login_required
def get_user_levels(user_id):
    user = User.query.get(user_id)
    return {
        'let_level': user.let_level,
        'zvezda_level': user.zvezda_level,
        'krin_level': user.krin_level
    }

@program_bp.route('/get_user_skills/<int:user_id>')
@login_required
def get_user_skills(user_id):
    skills = Skill.query.filter_by(user_id=user_id).all()
    if skills:
        skills_list = [{'name': skill.name, 'level': skill.level, 'date_got': skill.date_got.strftime('%Y-%m-%d')} for skill in skills]
        return jsonify(skills_list)
    else:
        return jsonify([])

@program_bp.route('/add_skill', methods=['POST'])
@login_required
def add_skill():
    data = request.get_json()
    user_id = data.get('user_id')
    name = data.get('name')
    level = data.get('level')
    date_got = datetime.strptime(data.get('date_got'), '%Y-%m-%d')

    new_skill = Skill(user_id=user_id, name=name, level=level, date_got=date_got)
    db.session.add(new_skill)
    db.session.commit()

    return jsonify({'message': 'Skill added successfully'}), 201