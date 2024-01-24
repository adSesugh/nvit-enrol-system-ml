from flask import Blueprint

guest_bp = Blueprint('guest', __name__, template_folder='templates')

from . import views