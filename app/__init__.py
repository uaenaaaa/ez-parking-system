from app.routes.auth import auth
from app.extension import mail
from os import getenv, makedirs, path
from logging import FileHandler, StreamHandler, basicConfig, getLogger, INFO
from flask import Flask
from flask_jwt_extended import JWTManager

def create_app():
    """Factory function to create the Flask app instance."""
    base_dir = path.abspath(path.dirname(__file__))
    template_dir = path.join(base_dir, 'templates')
    app = Flask(__name__, template_folder=template_dir)
    app.config['JWT_SECRET_KEY'] = getenv('JWT_SECRET_KEY')
    app.config['SECRET_KEY'] = getenv('SECRET_KEY')
    app.config['JWT_ACCESS_COOKIE_NAME'] = 'Authorization'
    app.config['JWT_SECRET_KEY'] = getenv('JWT_SECRET_KEY')
    app.config['MAIL_SERVER'] = getenv('MAIL_SERVER')
    app.config['MAIL_PORT'] = getenv('MAIL_PORT')
    app.config['MAIL_USE_TLS'] = getenv('MAIL_USE_TLS')
    app.config['MAIL_USERNAME'] = getenv('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = getenv('MAIL_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = getenv('MAIL_DEFAULT_SENDER')
    mail.init_app(app)
    JWTManager(app)
    makedirs(path.join(app.root_path, 'logs'), exist_ok=True)
    basicConfig(
        level=INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            FileHandler(path.join(app.root_path, 'logs', 'authentication.log')),
            StreamHandler()
        ]
    )
    app.register_blueprint(auth)
    getLogger()
    return app