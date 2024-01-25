from flask import render_template
from flask_login import login_required

from models.student import Student
from . import student_bp


@student_bp.route("/list")
@login_required
def list():
    return render_template("student/list.html")


@student_bp.route("/student/<int:student_id>")
@login_required
def post(student_id):
    return render_template("student/details.html", student_id=student_id)


@student_bp.route("/create")
@login_required
def register():
    return render_template("student/create.html")


@student_bp.route("/ablum")
@login_required
def album_list():
    students = Student.query.with_entities(
        Student.id,
        Student.means_of_id_no,
        Student.first_name,
        Student.last_name,
        Student.middle_name,
        Student.gender,
        Student.course_of_study,
        Student.student_no,
        Student.phone_number,
        Student.email,
        Student.lga_of_origin,
        Student.state_of_origin,
        Student.headshot
    ).order_by(Student.student_no).all()
    return render_template(
        "student/cards.html", students=students, title="Student Album"
    )
