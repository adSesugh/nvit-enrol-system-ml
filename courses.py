from app import create_app, db
from models.course import Course
from models.user import User
from utils.common import course_code

app = create_app()

courses = [
    "Applied AI and ML Engineering for Business Transformation and Real-world Applications",
    "Applied Cloud and DevOps Engineering",
    "Applied Data Science and Engineering",
    "Applied Enhanced Human-Centered UX/UI Product Design",
    "Applied Full-Stack Python Development Track",
    "Applied IT Technical Support & Operations Engineering"
]

with app.app_context():
    db.create_all()

    user = User.query.filter_by(id=1).first()

    for course in courses:
        db.session.add(Course(name=course, code=course_code(course)))
        db.session.commit()

    print("All courses added successfully!")



