# checklist_app/app.py

from flask import Flask, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, current_user
from config import Config

db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()
login_manager = LoginManager()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'

    import models

    from blueprints.auth import auth as auth_blueprint
    from blueprints.admin import admin as admin_blueprint
    from blueprints.main import main as main_blueprint
    from blueprints.checklists import checklists as checklists_blueprint
    
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(admin_blueprint, url_prefix='/admin')
    app.register_blueprint(main_blueprint)
    app.register_blueprint(checklists_blueprint)

    @app.route('/')
    def index():
        print(f"DEBUG: current_user.is_authenticated: {current_user.is_authenticated}")
        print(f"DEBUG: Session keys: {list(session.keys())}")
        if current_user.is_authenticated:
            return redirect(url_for('main.dashboard'))
        return redirect(url_for('auth.login'))

    # Rota temporária para limpar a sessão
    @app.route('/limpar_sessao')
    def limpar_sessao():
        session.clear()
        flash("Sessão limpa com sucesso!", "success")
        return redirect(url_for('auth.login'))

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)