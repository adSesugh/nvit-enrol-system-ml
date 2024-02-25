from app import create_app, db
from models.course import Course
from utils.common import course_code

instance = create_app()

courses = [
    "Applied AI and ML Engineering for Business Transformation and Real-world Applications",
    "Applied Cloud and DevOps Engineering",
    "Applied Data Science and Engineering",
    "Applied Enhanced Human-Centered UX/UI Product Design",
    "Applied Full-Stack Python Development Track",
    "Applied IT Technical Support & Operations Engineering"
]

with instance.app_context():
    db.create_all()

    for course in courses:
        db.session.add(Course(name=course, code=course_code(course)), user_id=1)
        db.session.commit()

    print("All courses added successfully!")



