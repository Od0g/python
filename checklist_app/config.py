import os

# Pega o caminho absoluto do diretório onde este arquivo está.
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    """Configurações base da aplicação."""
    # Chave secreta para proteger sessões e formulários contra CSRF.
    # Em produção, isso DEVE ser uma string aleatória e segura.
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'uma-chave-secreta-muito-dificil-de-adivinhar'
    
    # Configuração do banco de dados SQLAlchemy
    # Usa SQLite por padrão, criando um arquivo app.db no diretório raiz do projeto.
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
        
    # Desativa um recurso do SQLAlchemy que não usaremos e que consome recursos.
    SQLALCHEMY_TRACK_MODIFICATIONS = False