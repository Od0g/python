# app.py
from flask import Flask
from config import Config
from models import db, User # Importe também a classe User
from flask_migrate import Migrate
from flask_login import LoginManager # A importação correta
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
migrate = Migrate(app, db)

# Configuração do Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login' # Nome da rota para a página de login

# Função para carregar o usuário logado
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

from routes import *

if __name__ == '__main__':
    app.run(debug=True)