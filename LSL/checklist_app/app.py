from flask import Flask
from config import Config
from models import db
from flask_migrate import Migrate
import os
from dotenv import load_dotenv

load_dotenv() # Carrega variáveis do .env

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
migrate = Migrate(app, db)

from routes import * # Importa as rotas depois de inicializar db

if __name__ == '__main__':
    with app.app_context():
        db.create_all() # Cria as tabelas se não existirem
    app.run(debug=True)