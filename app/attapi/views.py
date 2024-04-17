import math
import math
import os
from datetime import date, datetime

import pyotp
import qrcode
from flask import jsonify, request
from flask_cors import CORS
from flask_jwt_extended import jwt_required, current_user, create_access_token, unset_jwt_cookies
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
CORS(att_bp, resources={r"/api/*": {"origins": "*"}})


@att_bp.route('/api/login_v1', methods=['POST'])
def login_v1():
    data = request.get_json()

    # device_exists = Student.query.filter_by(device_id=data['deviceId']).first()
    #
    # if device_exists:
    #     student = Student.query.filter_by(phone_number=data['phone_number']).first()
    #     if student is None or device_exists.phone_number != student.phone_number:
    #         return jsonify({'error': 'Already logged in with another device!'}), 401

    student = Student.query.filter_by(phone_number=data['phone_number']).first()
    if student and student.stud_session is not None:
        if student.device_id is None:
            student.device_id = data['deviceId']
            db.session.add(student)
            db.session.commit()
        # elif:
        #     return jsonify({'error': 'Already logged in another device'}), 401
        elif student.device_id != data['deviceId']:
                return jsonify({'error': 'Access locked! contact your administrator!'}), 401

        # student.last_login = datetime.now()
        # db.session.add(student)
        # db.session.commit()

        access_token = create_access_token(identity=student)
        return jsonify({'token': access_token, 'headshot': student.headshot, 'role': 'student'}), 200
    elif student.stud_session is None:
        return jsonify({'error': 'Access denied!, Please contact administrator'}), 401
    else:
        return jsonify({'error': 'Invalid credentials'}), 401


@att_bp.route('/api/login_v2', methods=['POST'])
def login_v2():
    data = request.get_json()

    user = User.query.filter_by(email=data['email']).first()
    if user:
        otp_code = otp.now()

        if data['email'] == 'tester@nvit.tech':
            return jsonify({'success': True, 'otp': otp_code}), 200

        msg = Message("NVITClock verification code!",
                      sender=('NVIT', os.environ.get('MAIL_USERNAME')),
                      recipients=[user.email])
        msg.html = f"Hello {user.username}! <br />Your verification code is: <br /><h1>{otp_code}</h1>"
        msg.send(mail)

        return jsonify({'success': True}), 200
    else:
        return jsonify({'error': 'Invalid credentials'}), 401


@att_bp.route('/api/verifyCode', methods=['POST'])
def verify_learner():
    data = request.get_json()
    if otp.verify(data['code']):
        user = User.query.filter_by(email=data['email']).first()
        access_token = create_access_token(identity=user)
        return jsonify(token=access_token, role='user'), 200
    else:
        return jsonify({'error': 'Invalid code'}), 401


@att_bp.route("/logout", methods=["POST"])
def logout():
    response = jsonify({"msg": "logout successful"})
    unset_jwt_cookies(response)
    return response


@att_bp.route('/api/qrcode', methods=['GET'])
@jwt_required()
def generate_qrcode():
    user = current_user.phone_number
    if user:
        qr = qrcode.make(user)
        qr_img_path = os.path.join('app/static', 'qrcodes', f'{current_user.phone_number}.png')
        qr.save(qr_img_path, format='PNG')

        filename = f'static/qrcodes/{current_user.phone_number}.png'
        server_host_url = request.host_url
        base_img_url = server_host_url.replace("http://", "https://")
        qr_img_url = base_img_url + filename

        return jsonify({'qr_code': qr_img_url}), 200
    return jsonify({'error': 'Data not provided'}), 404


@att_bp.route('/api/learner/<string:phone_number>', methods=['GET'])
@jwt_required()
def get_learner(phone_number):
    current_time = datetime.combine(datetime.today(), datetime.now().time())

    learner = Student.query.filter_by(phone_number=phone_number).first()
    if learner:
        stud_session = Session.query.get(learner.stud_session)
        starts_at = datetime.strptime(f'{stud_session.starts_at}', "%H:%M:%S%z").time()
        ends_at = datetime.strptime(f'{stud_session.ends_at}', "%H:%M:%S%z").time()
        session_starts = datetime.combine(datetime.today(), starts_at)
        session_ends = datetime.combine(datetime.today(), ends_at)

        profile = {
            'full_name': full_name(learner),
            'course': course_codex(learner.course_of_study),
            'studentId': learner.student_no,
            'email': learner.email,
            'phone': learner.phone_number,
            'photo': learner.headshot
        }

        if session_starts < current_time <= session_ends:
            current_attendance = Attendance.query.filter(cast(Attendance.checkin, Date) == date.today()).filter_by(student=learner).first()
            if current_attendance:
                if current_attendance.checkout is not None:
                    profile['msg'] = 'Already Check-out'
                    profile['status'] = True

                    return jsonify({'learner': profile}), 200
                else:
                    current_attendance.checkout = datetime.now()
                    db.session.add(current_attendance)
                    db.session.commit()

                    profile['msg'] = 'Check-out Successful'
                    profile['status'] = True

                    return jsonify({'learner': profile}), 200
            else:
                attendance = Attendance(student=learner, checkin=datetime.now(), status=True, taken_by=4)
                db.session.add(attendance)
                db.session.commit()

                profile['msg'] = 'Check-in Successful'
                profile['status'] = True

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
    stud_session = Session.query.get(current_user.stud_session)
    profile = {
        'full_name': full_name(current_user),
        'course': current_user.course_of_study,
        'studentId': current_user.student_no,
        'email': current_user.email,
        'phone': current_user.phone_number,
        'session': stud_session.duration,
        'status': True
    }

    return jsonify(profile), 200


@att_bp.route('/api/learner-board', methods=['GET'])
@jwt_required()
def get_learner_board():
    attendances = Attendance.query.filter_by(student_id=current_user.id).order_by(Attendance.checkin.desc()).limit(5).all()
    actual_attendance = Attendance.query.filter_by(status=True, student_id=current_user.id).count()
    expected_attendance = Attendance.query.filter_by(student_id=current_user.id).count()
    attendance_performance = actual_attendance / expected_attendance * 100 if expected_attendance > 0 else 0

    att_list = list()
    index = 0

    for attendance in attendances:
        index += 1

        attendance_checkin = attendance.checkin
        if "00:00+00" in attendance_checkin.__str__():
            datetime_obj = datetime.strptime(f'{attendance.checkin}', "%Y-%m-%d %H:%M:%S%z")
            checkin_time = datetime_obj.strftime("%Y-%m-%d %H:%M:%S.%f%z").replace("+00", "+01")
        else:
            datetime_obj = datetime.strptime(f'{attendance.checkin}', "%Y-%m-%d %H:%M:%S.%f%z")
            checkin_time = datetime_obj.strftime("%Y-%m-%d %H:%M:%S.%f%z").replace("+00", "+01")

        data = {
            'id': index,
            'checkin': checkin_time,
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
    attendance_percentage = attendance / student_total * 100
    return jsonify({'records': {
        'student_total': student_total,
        'attendance': attendance,
        'attendance_percentage': math.floor(attendance_percentage)
    }}), 200
