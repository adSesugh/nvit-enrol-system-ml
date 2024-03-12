import os
from datetime import timedelta

from flask import Flask, session, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from flask_migrate import Migrate
from dotenv import load_dotenv
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_mail import Mail

load_dotenv()

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
migrate = Migrate()
bcrypt = Bcrypt()
jwt = JWTManager()
mail = Mail()


def create_app():
    app = Flask(__name__)
    
    app.config['SECRET_KEY'] = os.urandom(64)

    # JWT config
    app.config["JWT_SECRET_KEY"] = os.urandom(64)
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=90)

    # Database config
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')

    # Mail setup
    app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER')
    app.config['MAIL_PORT'] = os.environ.get('MAIL_PORT')
    app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
    app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS')
    app.config['MAIL_USE_SSL'] = os.environ.get('MAIL_USE_SSL')

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    jwt.init_app(app)
    mail.init_app(app)

    # Import and register blueprints
    from .auth.views import auth_bp
    from .student.views import student_bp
    from .core.views import core_bp
    from .attapi.views import att_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(core_bp)
    app.register_blueprint(att_bp)

    @app.context_processor
    def inject_enumerate():
        return dict(enumerate=enumerate)

    return app


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
                return redirect(url_for('core.capture'))
