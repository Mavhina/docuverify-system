from flask import Flask


def create_app(template_folder=None):
    app = Flask(__name__, template_folder=template_folder or "templates")
    app.config['UPLOAD_FOLDER'] = 'uploads'
    app.secret_key = 'super-secret-key'

    from app.routes import main
    app.register_blueprint(main)

    return app
