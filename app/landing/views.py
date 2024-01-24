import os
from datetime import datetime

import cv2
from flask import flash, render_template, request, redirect, url_for
from flask_csv import send_csv
from flask_login import login_required, current_user

from . import guest_bp

from models.student import Student
from utils.common import extract_attendance, totalreg, datetoday2, add_attendance, identify_face, extract_faces, \
    getallusers, train_model, deletefolder, course_code, nimgs
from .. import db


@guest_bp.route('/')
def home():
    mats, names, courses, times, l = extract_attendance()
    return render_template('home.html', mats=mats, names=names, courses=courses, times=times, l=l, totalreg=totalreg(),
                           datetoday2=datetoday2)


@guest_bp.route('/attendance')
def attendance_list():
    mats, names, courses, times, l = extract_attendance()
    return render_template('attendance.html', mats=mats, names=names, courses=courses, times=times, l=l,
                           totalreg=totalreg)


## List users page
@guest_bp.route('/listusers')
def listusers():
    userlist, names, rolls, l = getallusers()
    return render_template('listusers.html', userlist=userlist, names=names, rolls=rolls, l=l, totalreg=totalreg(),
                           datetoday2=datetoday2)


## Delete functionality
@guest_bp.route('/deleteuser', methods=['GET'])
def deleteuser():
    duser = request.args.get('user')
    deletefolder('static/faces/' + duser)

    ## if all the face are deleted, delete the trained file...
    if os.listdir('static/faces/') == []:
        os.remove('static/face_recognition_model.pkl')

    try:
        train_model()
    except:
        pass

    userlist, names, rolls, l = getallusers()
    return render_template('listusers.html', userlist=userlist, names=names, rolls=rolls, l=l, totalreg=totalreg(),
                           datetoday2=datetoday2)


# Our main Face Recognition functionality.
# This function will run when we click on Take Attendance Button.
@guest_bp.route('/start', methods=['GET'])
def start():
    names, rolls, times, l = extract_attendance()

    if 'face_recognition_model.pkl' not in os.listdir('static'):
        return render_template('home.html', names=names, rolls=rolls, times=times, l=l, totalreg=totalreg(),
                               datetoday2=datetoday2,
                               mess='There is no trained model in the static folder. Please add a new face to continue.')

    ret = True
    cap = cv2.VideoCapture(0)
    while ret:
        ret, frame = cap.read()
        if len(extract_faces(frame)) > 0:
            (x, y, w, h) = extract_faces(frame)[0]
            cv2.rectangle(frame, (x, y), (x + w, y + h), (86, 32, 251), 1)
            cv2.rectangle(frame, (x, y), (x + w, y - 40), (86, 32, 251), -1)
            face = cv2.resize(frame[y:y + h, x:x + w], (50, 50))
            identified_person = identify_face(face.reshape(1, -1))[0]
            add_attendance(identified_person)
            cv2.putText(frame, f'{identified_person}', (x + 5, y - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.imshow('Attendance', frame)
        if cv2.waitKey(1) == 27:
            break
    cap.release()
    cv2.destroyAllWindows()
    numbers, names, courses, times, l = extract_attendance()
    return render_template('home.html', numbers=numbers, names=names, courses=courses, times=times, l=l,
                           totalreg=totalreg(),
                           datetoday2=datetoday2)


# A function to add a new user.
# This function will run when we add a new user.
@guest_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    data = request.form.to_dict()
    if request.method == 'POST':
        if data.get('first_name') == '' \
                or data.get('last_name') == '' \
                or data.get('email') == '' \
                or data.get('phone_number') == '' \
                or data.get('gender') is None \
                or data.get('state_of_origin') is None \
                or data.get('lga_of_origin') is None \
                or data.get('dob') == '' \
                or data.get('course_of_study') is None \
                or data.get('address') == '' \
                or data.get('means_of_id') == '' \
                or data.get('employment_status') is None \
                or data.get('level_of_education') is None \
                or data.get('disabled') is None \
                or data.get('emergency_full_name') == '' \
                or data.get('emergency_phone_number') == '' \
                or data.get('emergency_address') == '' \
                or data.get('guardian_first_name') == '' \
                or data.get('guardian_last_name') == '' \
                or data.get('guardian_phone_number') == '' \
                or data.get('terms') == '':

            flash('Error occured, Please try again')

            return render_template('home.html', mess='All data is required', student=data)

        student_exist = Student.query.filter_by(email=data.get('email')).first()  # Student.query.filter_by(email=data.get('email')).first()
        student_phone_number_exist = Student.query.filter_by(phone_number=data.get('phone_number')).first()
        print(student_exist)

        if student_exist or student_phone_number_exist:
            return render_template('home.html', mess="Applicant already exists", student=student_exist)

        if 'means_of_id_upload' in request.files:
            means_of_id = request.files['means_of_id_upload']
            if means_of_id:
                photo_path = os.path.join('app/static', 'uploads', means_of_id.filename)
                means_of_id.save(photo_path)
                data['means_of_id_upload'] = means_of_id.filename

        if 'signature' in request.files:
            signature = request.files['signature']
            if signature:
                signature_path = os.path.join('app/static', 'uploads', signature.filename)
                signature.save(signature_path)
                data['signature'] = f'uploads/{signature.filename}'

        year = abs(datetime.now().year) % 100
        code = course_code(data.get('course_of_study'))
        students = Student.query.all()
        student_count = len(students) + 1

        data['student_no'] = f'NVIT/{code}/{str(year)}/{str(student_count).zfill(6)}'  #'NVIT/' + str(year) + '/' + str(Student.query.count() + 1).zfill(6)

        data['terms'] = 'Yes' if data.get('terms') else 'No'
        data['user_id'] = current_user.id

        first_name = data['first_name']
        mat = str(student_count).zfill(6)

        student = Student(**data)
        db.session.add(student)
        db.session.commit()

        userimagefolder = 'app/static/faces/' + first_name + '_' + str(mat)
        if not os.path.isdir(userimagefolder):
            os.makedirs(userimagefolder)
        i, j = 0, 0
        cap = cv2.VideoCapture(0)
        while 1:
            _, frame = cap.read()
            faces = extract_faces(frame)
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 20), 2)
                cv2.putText(frame, f'Face Captured: {i}/{nimgs}', (30, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 20), 2, cv2.LINE_AA)
                if j % 5 == 0:
                    name = first_name + '_' + str(i) + '.jpg'
                    cv2.imwrite(userimagefolder + '/' + name, frame[y:y + h, x:x + w])
                    i += 1
                j += 1
            if j == nimgs * 5:
                break
            cv2.imshow('Face Capture', frame)
            if cv2.waitKey(2) == 27:
                break
        cap.release()
        cv2.destroyAllWindows()
        print('Training Model')
        train_model()

        return redirect(url_for('guest.home'))

    return redirect(url_for('guest.home'))


@guest_bp.route('/registered-students')
@login_required
def registered_students():
    # if not session.get('logged_in'):
    #     #students = db.session.execute(db.select(Student).order_by(Student.id)).scalars().all()
    #
    # return redirect(url_for('home'))
    students = Student.query.all()
    return render_template('student/studentlist.html', students=students)


@guest_bp.route('/students/<int:id>', methods=['GET'])
@login_required
def student(id):
    student = db.one_or_404(db.select(Student).filter_by(id=id))
    return render_template('student/detail.html', student=student)


@guest_bp.route('/students/album', methods=['GET'])
@login_required
def student_cards():
    students = db.session.execute(db.select(Student).order_by(Student.id)).scalars().all()
    return render_template('student/card.html', students=students)


@guest_bp.route('/download-list', methods=['GET'])
@login_required
def download_list():
    students = db.session.execute(db.select(Student).order_by(Student.id)).scalars().all()
    student_list = list()
    for student in students:
        data = {
            'id': student.id,
            'student_no': student.student_no,
            'first_name': student.first_name,
            'middle_name': student.middle_name,
            'last_name': student.last_name,
            'email': student.email,
            'phone_number': student.phone_number,
            'gender': student.gender,
            'state_of_origin': student.state_of_origin,
            'lga_of_origin': student.lga_of_origin,
            'dob': student.dob,
            'course_of_study': student.course_of_study,
            'address': student.address,
            'means_of_id': student.means_of_id,
            'means_of_id_upload': student.means_of_id_upload,
            'employment_status': student.employment_status,
            'level_of_education': student.level_of_education,
            'disabled': student.disabled,
            'disability_detail': student.disability_detail,
            'emergency_full_name': student.emergency_full_name,
            'emergency_email': student.emergency_email,
            'emergency_phone_number': student.emergency_phone_number,
            'emergency_address': student.emergency_address,
            'guardian_first_name': student.guardian_first_name,
            'guardian_last_name': student.guardian_last_name,
            'guardian_phone_number': student.guardian_phone_number,
            'guardian_email': student.guardian_email,
            'terms': student.terms
        }

        student_list.append(data)

    return send_csv(student_list, "students.csv",
                    ['id', 'student_no', 'first_name', 'middle_name', 'last_name', 'email', 'phone_number', 'gender',
                     'state_of_origin', 'lga_of_origin', 'dob', 'course_of_study', 'address', 'means_of_id',
                     'means_of_id_upload', 'employment_status', 'level_of_education', 'disabled', 'disability_detail',
                     'emergency_full_name', 'emergency_email', 'emergency_phone_number', 'emergency_address',
                     'guardian_first_name', 'guardian_last_name', 'guardian_phone_number', 'guardian_email', 'terms'])
