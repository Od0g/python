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


    # Configuração de E-mail
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.googlemail.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None or True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or 'seu-email@gmail.com'  # <-- SEU E-MAIL AQUI
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or 'sua-senha-de-app'   # <-- SUA SENHA DE APP AQUI
    ADMINS = ['email-do-gestor@exemplo.com'] # E-mail que receberá os alertas