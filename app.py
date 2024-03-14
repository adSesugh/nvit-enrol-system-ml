from werkzeug.middleware.proxy_fix import ProxyFix

from app import create_app, scheduler
from utils.cronjob import attendance_marker

app = create_app()
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_host=1)

if __name__ == '__main__':
    from waitress import serve

    # scheduler.start()
    # scheduler.add_job(attendance_marker, 'cron', hour=6, minute=43, id="AttendanceMarker")

    serve(app, host='0.0.0.0', port=5000)
