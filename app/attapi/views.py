import math
import math
import os
from datetime import date, datetime

import pyotp
import qrcode
from flask import jsonify, request
from flask_jwt_extended import jwt_required, current_user, create_access_token
from flask_mail import Message
from sqlalchemy import Date, cast

from app import mail, db
from models.attendance import Attendance
from models.session import Session
from models.student import Student
from models.user import User
from utils.common import full_name, course_codex
from . import att_bp

secret_key = pyotp.random_base32()
otp = pyotp.TOTP(secret_key, interval=120, digits=4)


@att_bp.route('/api/login_v1', methods=['POST'])
def login_v1():
    data = request.get_json()
    print(data)
    student = Student.query.filter_by(phone_number=data['phone_number']).first()
    print(student)
    if student:
        access_token = create_access_token(identity=student)
        return jsonify({'token': access_token, 'headshot': student.headshot, 'role': 'student'}), 200
    else:
        return jsonify({'error': 'Invalid credentials'}), 401


@att_bp.route('/api/login_v2', methods=['POST'])
def login_v2():
    data = request.get_json()

    user = User.query.filter_by(email=data['email']).first()
    if user:
        otp_code = otp.now()
        print(otp_code)
        msg = Message("VerifyAtt verification code!",
                      sender="noreply@nvit.tech",
                      recipients=[user.email, 'asesugh@gmail.com'])
        msg.html = f"Hello {user.username}! <br />Your verification code is: <br /><h1>{otp_code}</h1>"
        msg.send(mail)

        return jsonify({'success': True}), 200
    else:
        return jsonify({'error': 'Invalid credentials'}), 401


@att_bp.route('/api/verifyCode', methods=['POST'])
def verify_learner():
    data = request.get_json()
    print(data)
    if otp.verify(data['code']):
        user = User.query.filter_by(email=data['email']).first()
        access_token = create_access_token(identity=user)
        return jsonify(token=access_token, role='user'), 200
    else:
        return jsonify({'error': 'Invalid code'}), 401


@att_bp.route('/api/qrcode', methods=['GET'])
@jwt_required()
def generate_qrcode():
    user = current_user.phone_number
    if user:
        qr = qrcode.make(user)
        qr_img_path = os.path.join('app/static', 'qrcodes', f'{current_user.phone_number}.png')
        qr.resize((200, 200))
        qr.save(qr_img_path, format='PNG')

        filename = f'static/qrcodes/{current_user.phone_number}.png'
        qr_img_url = request.host_url + filename

        return jsonify({'qr_code': qr_img_url}), 200
    return jsonify({'error': 'Data not provided'}), 404


@att_bp.route('/api/learner/<string:phone_number>', methods=['GET'])
@jwt_required()
def get_learner(phone_number):
    current_time = datetime.combine(datetime.today(), datetime.now().time())

    learner = Student.query.filter_by(phone_number=phone_number).first()
    stud_session = Session.query.get(learner.stud_session)

    starts_at = datetime.strptime(f'{stud_session.starts_at}', "%H:%M:%S%z").time()
    session_starts = datetime.combine(datetime.today(), starts_at)
    ends_at = datetime.strptime(f'{stud_session.ends_at}', "%H:%M:%S%z").time()
    session_ends = datetime.combine(datetime.today(), ends_at)

    profile = {
        'full_name': full_name(learner),
        'course': course_codex(learner.course_of_study),
        'studentId': learner.student_no,
        'email': learner.email,
        'phone': learner.phone_number,
        'status': True,
        'photo': learner.headshot
    }
    if session_starts <= current_time <= session_ends:
        current_attendance = Attendance.query.filter((cast(Attendance.checkin, Date) == date.today()) & (Attendance.checkin is not None)).filter_by(student=learner).first()
        if current_attendance:
            if current_attendance.checkout is not None:
                profile['msg'] = 'Already Check-out'
                return jsonify({'learner': profile}), 200

            current_attendance.checkout = datetime.now()
            db.session.add(current_attendance)
            db.session.commit()

            profile['msg'] = 'Check-out Successful'
            return jsonify({'learner': profile}), 200
        else:
            attendance = Attendance(student=learner, checkin=datetime.now(), status=True, taken_by=current_user.id)
            db.session.add(attendance)
            db.session.commit()
            if learner:
                profile['msg'] = 'Check-in Successful'
                return jsonify({'learner': profile}), 200
    else:
        profile['session'] = stud_session.duration
        profile['status'] = False
        profile['msg'] = 'Capture unsuccessful'
        return jsonify({'learner': profile}), 200

    return jsonify({'error': 'Learner not found'}), 404


@att_bp.route('/api/profile', methods=['GET'])
@jwt_required()
def get_profile():
    profile = {
        'full_name': full_name(current_user),
        'course': current_user.course_of_study,
        'studentId': current_user.student_no,
        'email': current_user.email,
        'phone': current_user.phone_number,
        'status': True
    }

    return jsonify(profile), 200


@att_bp.route('/api/learner-board', methods=['GET'])
@jwt_required()
def get_learner_board():
    attendances = Attendance.query.filter_by(student_id=current_user.id).order_by(Attendance.id.desc()).limit(5).all()
    actual_attendance = Attendance.query.filter_by(status=True, student_id=current_user.id).count()
    expected_attendance = Attendance.query.filter_by(student_id=current_user.id).count()
    attendance_performance = actual_attendance/expected_attendance * 100

    att_list = list()
    index = 0
    for attendance in attendances:
        index += 1
        data = {
            'id': index,
            'checkin': attendance.checkin,
            'status': attendance.status
        }
        att_list.append(data)

    records = {
        'actual_attendance': actual_attendance,
        'expected_attendance': expected_attendance,
        'attendance_performance': math.floor(attendance_performance),
        'attendances': att_list
    }

    return jsonify(records), 200


@att_bp.route('/api/staff-board', methods=['GET'])
@jwt_required()
def get_staff_board():
    student_total = Student.query.filter(Student.employment_status != 'Employed').count()
    attendance = Attendance.query.filter(cast(Attendance.checkin, Date) == date.today()).count()
    attendance_percentage = attendance/student_total*100
    return jsonify({'records': {
        'student_total': student_total,
        'attendance': attendance,
        'attendance_percentage': math.floor(attendance_percentage)
    }}), 200