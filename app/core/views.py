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
    disability = db.session.query(Student.disabled, func.count().label('count_disabled')).group_by(Student.disabled).all()
    male_disabled = Student.query.filter_by(disabled='yes', gender='Male').count()
    female_disabled = Student.query.filter_by(disabled='yes', gender='Female').count()

    labels = list()
    values = list()
    courses = list()
    pwd_labels = list()
    male = list()
    female = list()

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

    # result = db.session.query(
    #     Student.disabled,
    #     Student.gender,
    #     Student.course_of_study,
    #     Student.employment_status,
    #     func.count().label('count')
    # ).group_by(
    #     Student.disabled,
    #     Student.gender,
    #     Student.course_of_study,
    #     Student.employment_status
    # ).all()

    # gender_courses_data = [
    #     {'gender': row[0], 'course_of_study': course_code(row[1]), 'count': row[2]}
    #     for row in result_gender_courses
    # ]
    return render_template('dashboard.html', records=data)
