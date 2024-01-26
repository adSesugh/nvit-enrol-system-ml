from flask import session, request, redirect, url_for
from flask_login import current_user
from app import create_app

app = create_app()


@app.before_request
def check_user_role():
    # Check if the user is authenticated and has a role stored in the session
    if current_user.is_authenticated and 'user_role' in session:
        user_role = session['user_role']

        # Redirect users based on their role
        if user_role == 'admin':
            if request.endpoint and 'admin' not in request.endpoint:
                return redirect(url_for('core.dashboard'))
        elif user_role == 'user':
            if request.endpoint and 'user' not in request.endpoint:
                return redirect(url_for('guest.capture'))