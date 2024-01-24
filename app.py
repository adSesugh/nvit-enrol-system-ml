from flask import render_template

from app import create_app

app = create_app()


@app.context_processor
def inject_enumerate():
    return dict(enumerate=enumerate)


if __name__ == '__main__':
    app.run(debug=True)