from flask import render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user
from . import auth_bp

from flask import render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from app import db, bcrypt, login_manager
from .forms import RegistrationForm, LoginForm
from . import auth_bp
from models.user import User


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    print(form)
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', title='Register', form=form)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            # Store the intended URL in the session
            next_url = request.args.get('next')
            if not next_url or not next_url.startswith('/'):
                next_url = url_for('core.dashboard')
            session['next_url'] = next_url
            session['user_role'] = user.role

            return redirect(next_url)
        else:
            flash('Login unsuccessful. Please check email and password.', 'danger')
    return render_template('auth/login.html', title='Login', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@auth_bp.route('/profile')
@login_required
def profile():
    return render_template('auth/profile.html', title='Profile')
