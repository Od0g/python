import os

# Pega o caminho absoluto do diretório do arquivo config.py
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    # Chave secreta para proteger sessões e cookies. Mude isso para um valor aleatório!
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'voce-nunca-vai-adivinhar'
    
    # Configuração do banco de dados SQLite
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False