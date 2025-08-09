# app.py
from flask import Flask
import base64 # Importe a biblioteca base64
from config import Config
from models import db, User # Importe também a classe User
from flask_migrate import Migrate
from flask_login import LoginManager # A importação correta
from flask_mail import Mail # Importe a classe Mail
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
migrate = Migrate(app, db)
mail = Mail(app) # Inicialize a extensão Flask-Mail

# Configuração do Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login' # Nome da rota para a página de login

def b64encode_filter(data):
    return base64.b64encode(data).decode('utf-8')

app.jinja_env.filters['b64encode'] = b64encode_filter

# Função para carregar o usuário logado
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

from routes import *

if __name__ == '__main__':
    app.run(debug=True)