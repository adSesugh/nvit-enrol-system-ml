from datetime import datetime

from app import db


class Gallery(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False, unique=True)
    created = db.Column(db.DateTime(timezone=True),
                        default=datetime.now())
    updated = db.Column(db.DateTime(timezone=True), default=datetime.now(),
                        onupdate=datetime.now())
    title = db.Column(db.String(191), nullable=True)
    type = db.Column(db.String(100))
    media_url = db.Column(db.String(254))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
