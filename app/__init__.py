import os
from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'
bcrypt = Bcrypt()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # LINHA DE DEPURAÇÃO: VAI MOSTRAR O CAMINHO DO BANCO NO TERMINAL
    print(f"--- DATABASE URI: {app.config['SQLALCHEMY_DATABASE_URI']} ---")

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    bcrypt.init_app(app)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.routes import bp as main_bp
    app.register_blueprint(main_bp)
    
    qr_code_folder = os.path.join(app.static_folder, 'qrcodes')
    if not os.path.exists(qr_code_folder):
        os.makedirs(qr_code_folder)

    return app

from app import models