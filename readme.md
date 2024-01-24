## flask --app yourapplication run

### Environment Setup
    export FLASK_APP=app.py
    export FLASK_ENV=development
    flask run

### For debug mode
    flask run --debug

### Migrate - Flask-Migrate
    flask db init
    flask db migrate -m "Initial migration"
    flask db upgrade

### Database URL
    DATABASE_URL=postgresql://<username>:<password>@<host>:<port>/<database_name>
