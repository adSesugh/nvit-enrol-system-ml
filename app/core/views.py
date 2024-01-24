from flask import render_template
from flask_login import login_required

from . import core_bp


@core_bp.route('/', methods=['GET'])
@login_required
def dashboard():
    print('hello')
    return render_template('dashboard.html')