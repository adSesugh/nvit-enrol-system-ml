from flask import Blueprint, jsonify

from models.student import Student
from models.user import User
from .. import jwt

att_bp = Blueprint('attendance', __name__)

from . import views


@jwt.user_identity_loader
def user_identity_lookup(user):
    return user.id


@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    return Student.query.filter_by(id=identity).one_or_none()