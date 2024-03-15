import pandas
import pandas as pd
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from models.attendance import Attendance
from models.student import Student
from . import student_bp
from .form import AttendanceForm
from .. import db


@student_bp.route("/list")
@login_required
def list():
    return render_template("student/list.html")


@student_bp.route("/student/<int:student_id>")
@login_required
def post(student_id):
    return render_template("student/details.html", student_id=student_id)


@student_bp.route("/create", methods=["GET", "POST"])
@login_required
def register():
    return render_template("student/create.html")


@student_bp.route("/album", methods=["GET"])
@login_required
def album_list():
    students = Student.query.filter((Student.employment_status != 'Employed')).order_by(Student.id).all()  #db.session.execute(db.select(Student).order_by(Student.id)).scalars().all()
    return render_template(
        "student/card.html", students=students, title="Student Album"
    )


@student_bp.route("/wb-album-for-male", methods=["GET"])
@login_required
def wb_album():
    students = Student.query.filter((Student.employment_status != 'Employed') & (Student.gender=='Male') & (Student.disabled=='no')).order_by(Student.id).all()  #db.session.execute(db.select(Student).order_by(Student.id)).scalars().all()
    return render_template(
        "student/foralbum.html", students=students, title="Student Album"
    )


@student_bp.route("/wb-album-for-female", methods=["GET"])
@login_required
def wb_album_female():
    students = Student.query.filter((Student.employment_status != 'Employed') & (Student.gender=='Female')).order_by(Student.id).all()  #db.session.execute(db.select(Student).order_by(Student.id)).scalars().all()
    return render_template(
        "student/foralbum.html", students=students, title="Student Album"
    )


@student_bp.route("/wb-album-for-disabled", methods=["GET"])
@login_required
def wb_album_disabled():
    students = Student.query.filter((Student.employment_status != 'Employed') & (Student.disabled=='yes')).order_by(Student.id).all()  #db.session.execute(db.select(Student).order_by(Student.id)).scalars().all()
    return render_template(
        "student/foralbum.html", students=students, title="Student Album"
    )


@student_bp.route("/attendance", methods=["GET"])
@login_required
def attendance_list():
    attendances = Attendance.query.all()

    return render_template("attendance/index.html", attendances=attendances)


@student_bp.route("/attendance/upload", methods=["GET", "POST"])
@login_required
def attendance_upload():
    form = AttendanceForm()
    if form.validate_on_submit():
        print('here')
        try:
            file = form.upload.data
            print(file)
            if file.filename.endswith('.xlsx'):
                df = pd.read_excel(file)
            elif file.filename.endswith('.csv'):
                df = pd.read_csv(file)
            else:
                raise ValueError("Invalid file format. Supported formats: .xlsx, .csv")

            for _, row in df.iterrows():
                student = Student.query.with_entities(Student.id).filter_by(phone_number=row[0]).first()
                attendance = Attendance(
                    student_id=student.id,
                    status=True if row[1] == '1' else False,
                    taken_by=current_user.id
                )
                db.session.add(attendance)
                db.session.commit()

                flash('Your account has been created! You are now able to log in.', 'success')
                return redirect(url_for('attendance_list'))

        except Exception as e:
            return render_template('attendance/create.html', str(e))

    return render_template('attendance/create.html', form=form)