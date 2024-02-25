from app import db, create_app
from models.session import StudentSession

seed = create_app()

with seed.app_context():
    db.create_all()

    morning = StudentSession(name='Morning', duration='7:00AM - 10:00AM', user_id=1)
    morning_afternoon = StudentSession(name='Morning Afternoon', duration='10:00AM - 1:00PM', user_id=1)
    afternoon = StudentSession(name='Afternoon', duration='1:00PM - 4:00PM', user_id=1)
    evening = StudentSession(name='Evening', duration='4:00PM - 7:00PM', user_id=1)

    db.session.add_all([morning, morning_afternoon, afternoon, evening])
    db.session.commit()

    print('Session added successfully!')