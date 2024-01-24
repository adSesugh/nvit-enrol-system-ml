from flask import render_template
from flask_login import login_required

from models.student import Student
from . import core_bp


@core_bp.route('/', methods=['GET'])
@login_required
def dashboard():
    students = len(Student.query.all())
    data = {
        'captured': students
    }
    return render_template('dashboard.html', records=data)