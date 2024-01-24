from datetime import datetime

from sqlalchemy.dialects.postgresql import TEXT

from app import db


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

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __repr__(self):
        return "<%r> <%r>" % (self.first_name, self.last_name)

    def full_name(self):
        if self.middle_name != '':
            return "%s %s %s" % (self.first_name, self.middle_name, self.last_name)

        return "%s %s" % (self.first_name, self.last_name)