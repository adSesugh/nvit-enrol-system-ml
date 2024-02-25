from datetime import datetime

from app import db


class StudentSession(db.Model):
    __tablename__ = 'sessions'

    id = db.Column(db.Integer, primary_key=True, nullable=False, unique=True)
    created = db.Column(db.DateTime(timezone=True),
                        default=datetime.now())
    updated = db.Column(db.DateTime(timezone=True), default=datetime.now(),
                        onupdate=datetime.now())

    name = db.Column(db.String(100), nullable=False, unique=True)
    duration = db.Column(db.String(20), unique=True, nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    def __repr__(self):
        return '%r %r' % (self.name, self.duration)