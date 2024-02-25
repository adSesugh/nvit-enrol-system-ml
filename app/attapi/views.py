
import os

import pyotp
import qrcode
from flask import jsonify, request
from flask_jwt_extended import jwt_required, current_user, create_access_token
from flask_mail import Message
from sqlalchemy import Date, cast

from app import mail
from models.attendance import Attendance
from models.student import Student
from models.user import User
from utils.common import full_name, course_codex
from . import att_bp
from datetime import date

secret_key = pyotp.random_base32()
otp = pyotp.TOTP(secret_key, interval=120, digits=4)


@att_bp.route('/api/login_v1', methods=['POST'])
def login_v1():
    data = request.get_json()
    student = Student.query.filter_by(phone_number=data['phone_number']).first()
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
    learner = Student.query.filter_by(phone_number=phone_number).first()
    profile = {
        'full_name': full_name(learner),
        'course': course_codex(learner.course_of_study),
        'studentId': learner.student_no,
        'email': learner.email,
        'phone': learner.phone_number,
        'status': True,
        'photo': learner.headshot
    }
    if learner:
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
    return jsonify({'records': True}), 200


@att_bp.route('/api/staff-board', methods=['GET'])
@jwt_required()
def get_staff_board():
    student_total = Student.query.filter(Student.employment_status != 'Employed').count()
    attendance = Attendance.query.filter(cast(Attendance.checkin, Date) == date.today()).count()
    attendance_percentage = attendance/student_total*100
    return jsonify({'records': {
        'student_total': student_total,
        'attendance': attendance,
        'attendance_percentage': attendance_percentage
    }}), 200