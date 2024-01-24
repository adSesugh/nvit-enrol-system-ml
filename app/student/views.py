from flask import render_template
from . import student_bp


@student_bp.route('/list')
def list():
    return render_template('student/list.html')


@student_bp.route('/student/<int:student_id>')
def post(student_id):
    return render_template('student/details.html', student_id=student_id)


@student_bp.route('/create')
def register():
    return render_template('student/create.html')