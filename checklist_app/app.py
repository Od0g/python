from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import Config

# Inicialização das extensões (ainda não vinculadas a um app específico)
db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
# Define a view de login. Se um usuário não logado tentar acessar uma página protegida,
# o Flask-Login o redirecionará para esta rota.
login.login_view = 'auth.login' 
login.login_message = 'Por favor, faça login para acessar esta página.'

def create_app(config_class=Config):
    """
    Função Factory para criar a instância da aplicação Flask.
    """
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Vincula as extensões à instância da aplicação
    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)

    # Registro de Blueprints (serão criados depois para organizar as rotas)
    # Exemplo:
    # from app.auth import bp as auth_bp
    # app.register_blueprint(auth_bp, url_prefix='/auth')

    # Rota de teste inicial
    @app.route('/test')
    def test_page():
        return '<h1>Configuração inicial funcionando!</h1>'

    return app

# Importa os models para que o Flask-Migrate possa encontrá-los.
# É importante importar depois da inicialização do 'db'.
from models import Usuario # Este import dará erro agora, mas funcionará no próximo bloco.

# O user_loader é necessário para o Flask-Login. Ele carrega um usuário a partir do ID
# armazenado na sessão.
@login.user_loader
def load_user(id):
    return Usuario.query.get(int(id))