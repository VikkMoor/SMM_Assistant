
import os

from dotenv import load_dotenv
from flask import Flask, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

load_dotenv()

db = SQLAlchemy()
bcrypt = Bcrypt()


def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

    if not app.config['SECRET_KEY']:
        raise RuntimeError('SECRET_KEY is not configured')

    os.makedirs(app.instance_path, exist_ok=True)

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

    db.init_app(app)
    bcrypt.init_app(app)

    from app.auth import auth_bp
    from app.smm import smm_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(smm_bp, url_prefix='/smm')

    @app.route('/')
    def index():
        return redirect(url_for('smm.dashboard'))

    with app.app_context():
        db.create_all()

    return app
