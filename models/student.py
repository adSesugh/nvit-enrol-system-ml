from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from sqlalchemy.dialects.postgresql import TEXT

from app import db
from utils.common import course_list_for_album, course_short


class STATUS(Enum):
    PENDING = "Pending",
    APPROVED = "Approved"
    REJECTED = "Rejected"


class Student(db.Model):
    __tablename__ = 'students'

    id = db.Column(db.Integer, primary_key=True, nullable=False, unique=True)
    created = db.Column(db.DateTime(timezone=True),
                        default=datetime.now())
    updated = db.Column(db.DateTime(timezone=True), default=datetime.now(),
                        onupdate=datetime.now())

    student_no = db.Column(db.String(60), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    middle_name = db.Column(db.String(100), nullable=True)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    phone_number = db.Column(db.String(20), unique=True)
    gender = db.Column(db.String(15))
    state_of_origin = db.Column(db.String(70))
    lga_of_origin = db.Column(db.String(100))
    dob = db.Column(db.Date)
    course_of_study = db.Column(db.String(190))
    address = db.Column(db.String(190))
    means_of_id = db.Column(db.String(100))
    means_of_id_no = db.Column(db.String(100), unique=True)
    means_of_id_upload = db.Column(db.String(191), nullable=True)
    employment_status = db.Column(db.String(100))
    level_of_education = db.Column(db.String(100))
    disabled = db.Column(db.String(5))
    disability_detail = db.Column(db.String(1000), nullable=True)

    emergency_full_name = db.Column(db.String(150), nullable=False)
    emergency_email = db.Column(db.String(100), nullable=False)
    emergency_phone_number = db.Column(db.String(20))
    emergency_address = db.Column(db.String(150), nullable=False)

    guardian_first_name = db.Column(db.String(60), nullable=False)
    guardian_last_name = db.Column(db.String(60), nullable=False)
    guardian_email = db.Column(db.String(100), nullable=False)
    guardian_phone_number = db.Column(db.String(20))
    guardian_address = db.Column(db.String(191), nullable=True)

    signature = db.Column(db.String(200), nullable=False)
    headshot = db.Column(TEXT, nullable=False)

    terms = db.Column(db.String(10), default=True, nullable=True)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    record_sealed = db.Column(db.Boolean, default=False)
    confirm_nin = db.Column(db.Boolean, default=False)
    reason = db.Column(db.String(100), nullable=True)
    is_approved = db.Column(db.Boolean, default=False)
    stud_session = db.Column(db.Integer, db.ForeignKey('sessions.id'), nullable=True)
    device_id = db.Column(db.String(100), nullable=True)
    status = db.Column(db.String(100), nullable=True, default='Pending')

    attendances = db.relationship('Attendance', backref='student', lazy='dynamic')

    def full_name(self):
        if self.middle_name != '':
            return "%s %s %s" % (self.first_name, self.middle_name, self.last_name)

        return "%s %s" % (self.first_name, self.last_name)

    def get_name_initial(self):
        if self.middle_name != '':
            return f"{self.first_name} {self.middle_name[0]}. {self.last_name}"

        return "%s %s" % (self.first_name, self.last_name)

    def student_course(self):
        code = ''
        for cor in course_list_for_album:
            if cor['name'] == self.course_of_study:
                code = cor['code']
                break
        return code


    def student_card_course(self):
        code = ''
        for cor in course_short:
            if cor['name'] == self.course_of_study:
                code = cor['code']
                break
        return code
