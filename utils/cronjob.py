from datetime import datetime

from sqlalchemy import cast, Date

from app import scheduler, db, create_app
from models.attendance import Attendance
from models.session import Session
from models.student import Student

app = create_app()


def attendance_marker():
    with app.app_context():
        students = Student.query.order_by(Student.id).all()
        for student in students:
            attendance = Attendance.query.filter(
                (cast(Attendance.checkin, Date) == datetime.now().date())).filter_by(
                student_id=student.id, checkout=None).first()
            if attendance:
                attendance.status = False
                attendance.checkout = attendance.checkin
                db.session.add(attendance)
                db.session.commit()
            else:
                stud_session = Session.query.get(student.stud_session)
                if stud_session:
                    starts_at = datetime.strptime(f'{stud_session.starts_at}', "%H:%M:%S%z").time()
                    session_starts = datetime.combine(datetime(2024, 3, 8), starts_at)

                    absent = Attendance(student_id=student.id, status=False, checkin=session_starts,
                                        checkout=session_starts, taken_by=3)
                    db.session.add(absent)
                    db.session.commit()

    with open('jobs.csv', 'a', newline='') as csvfile:
        print(f"Scheduled job executed - {datetime.now()}", file=csvfile)


def my_cron_job():
    with open('test.txt', 'w') as f:
        print("CronJob started", file=f)
    print("This is a cron job running every 5 minutes")
