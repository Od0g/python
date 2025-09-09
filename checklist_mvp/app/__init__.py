from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

# Cria a instância da aplicação principal
app = Flask(__name__)
app.config.from_object(Config)

# Inicializa os plugins diretamente com a 'app'
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'

# A importação de models e routes fica no final para evitar importações circulares
from app import routes, models