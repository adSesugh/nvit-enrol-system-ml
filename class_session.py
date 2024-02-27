from app import db, create_app
from models.session import Session

seed = create_app()

with seed.app_context():
    db.create_all()

    morning = Session(name='Morning', duration='7:00AM - 10:00AM', starts_at='7:00', ends_at='10:00', user_id=1)
    morning_afternoon = Session(name='Morning Afternoon', duration='10:00AM - 1:00PM', starts_at='10:00', ends_at='13:00', user_id=1)
    afternoon = Session(name='Afternoon', duration='1:00PM - 4:00PM', starts_at='13:00', ends_at='16:00', user_id=1)
    evening = Session(name='Evening', duration='4:00PM - 7:00PM', starts_at='16:00', ends_at='19:00', user_id=1)

    db.session.add_all([morning, morning_afternoon, afternoon, evening])
    db.session.commit()

    print('Session added successfully!')