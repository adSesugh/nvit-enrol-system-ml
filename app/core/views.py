from flask import render_template
from flask_login import login_required, current_user
from sqlalchemy import func

from models.student import Student
from utils.common import course_code
from . import core_bp
from .. import db


@core_bp.route('/', methods=['GET'])
@login_required
def dashboard():

    if current_user.role == 'user' and current_user.username != 'worldbank':
        return render_template('home.html')

    students = len(Student.query.all())
    female_count = Student.query.filter_by(gender='Female').count()
    male_count = Student.query.filter_by(gender='Male').count()
    grouped = Student.query.with_entities(Student.course_of_study, func.count(Student.course_of_study)).group_by(
        Student.course_of_study).all()
    male_disabled = Student.query.filter_by(disabled='yes', gender='Male').count()
    female_disabled = Student.query.filter_by(disabled='yes', gender='Female').count()

    result = db.session.query(
        Student.disabled,
        Student.gender,
        Student.course_of_study,
        func.count().label('count')
    ).group_by(
        Student.disabled,
        Student.gender,
        Student.course_of_study
    ).all()

    # Convert the result to a list of dictionaries
    stats_data = [
        {'disabled': row[0], 'gender': row[1], 'course_of_study': course_code(row[2]), 'count': row[3]}
        for row in result
    ]

    labels = list()
    values = list()
    courses = list()

    for course in grouped:
        code = course_code(course[0])
        labels.append(code)
        values.append(course[1])
        courses.append(course[0])

    data = {
        'captured': students,
        'stats': {
            'labels': labels,
            'data': values,
            'courses': courses
        },
        'female_count': female_count,
        'male_count': male_count,
        'female_disabled': female_disabled,
        'male_disabled': male_disabled
    }

    return render_template('dashboard.html', records=data, stats_data=stats_data)
