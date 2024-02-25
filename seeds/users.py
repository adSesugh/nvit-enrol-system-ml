from app import create_app, db, bcrypt
from models.user import User

app = create_app()

with app.app_context():
    # Create tables if not exists
    db.create_all()

    admin = hashed_password = bcrypt.generate_password_hash('ad&#min@12').decode('utf-8')
    worldbank = hashed_password = bcrypt.generate_password_hash('world@#ba&nk&1').decode('utf-8')
    enroller = hashed_password = bcrypt.generate_password_hash('enroller@123').decode('utf-8')

    # Seed data
    user1 = User(full_name='Administrator', username='admin', email='admin@nvit.tech', password=admin, role='admin')
    user2 = User(full_name='World Bank', username='worldbank', email='wb@nvit.tech', password=worldbank, role='user')
    user3 = User(full_name='Sesugh Agbadu', username='enroller', email='enroller@nvit.tech', password=enroller, role='user')

    # Add users to the session
    db.session.add_all([user1, user2, user3])

    # Commit the changes
    db.session.commit()

    print('Seed data added successfully!')