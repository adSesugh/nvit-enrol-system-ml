from datetime import datetime

from app import db
from models.student import Student


class Attendance(db.Model):
    __tablename__ = 'attendances'

    id = db.Column(db.Integer, primary_key=True, nullable=False, unique=True)
    updated = db.Column(db.DateTime(timezone=True), default=datetime.now(),
                        onupdate=datetime.now())

    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    status = db.Column(db.Boolean, default=False, nullable=False)
    checkin = db.Column(db.DateTime(timezone=True), default=datetime.now())
    checkout = db.Column(db.DateTime(timezone=True), nullable=True)
    taken_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    def __repr__(self):
        student = Student.query.get(self.student_id)
        return f'{student.last_name} {student.first_name}'
