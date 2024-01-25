from flask import render_template
from flask_login import login_required, current_user
from sqlalchemy import func

from models.student import Student
from utils.common import course_code
from . import core_bp


@core_bp.route('/', methods=['GET'])
@login_required
def dashboard():
    #global grouped, female_count, male_count
    students = len(Student.query.all())

    if current_user.is_authenticated and current_user.role == 'user' and current_user.username == 'worldbank':
        pass
        #print(grouped)

    female_count = Student.query.filter_by(gender='Female').count()
    male_count = Student.query.filter_by(gender='Male').count()
    grouped = Student.query.with_entities(Student.course_of_study, func.count(Student.course_of_study)).group_by(
        Student.course_of_study).all()

    labels = list()
    values = list()
    courses = list()

    for course in grouped:
        code = course_code(course[0])
        labels.append(code)
        values.append(course[1])
        print(f'course val: {course[1]}')
        courses.append(course[0])

    print(values)
    data = {
        'captured': students,
        'stats': {
            'labels': labels,
            'data': values,
            'courses': courses
        },
        'female_count': female_count,
        'male_count': male_count
    }
    return render_template('dashboard.html', records=data)