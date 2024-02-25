from datetime import datetime

from app import db


class Course(db.Model):
    __tablename__ = 'courses'

    id = db.Column(db.Integer, primary_key=True, nullable=False, unique=True)
    created = db.Column(db.DateTime(timezone=True),
                        default=datetime.now())
    updated = db.Column(db.DateTime(timezone=True), default=datetime.now(),
                        onupdate=datetime.now())

    code = db.Column(db.String(80), unique=True, nullable=False)
    name = db.Column(db.String(196), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

