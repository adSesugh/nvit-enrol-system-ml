from app import create_app
from werkzeug.middleware.proxy_fix import ProxyFix

app = create_app()
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_host=1)

if __name__ == '__main__':
    from waitress import serve
    serve(app, host='0.0.0.0', port=5000, url_scheme='https')