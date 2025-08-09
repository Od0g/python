import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'uma_chave_secreta_muito_segura'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///site.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Configurações do Flask-Mail
    MAIL_SERVER = 'smtp.gmail.com' # Use o servidor SMTP do seu provedor de e-mail
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('EMAIL_USER')
    MAIL_PASSWORD = os.environ.get('EMAIL_PASS')
    MAIL_DEFAULT_SENDER = 'seu-email@dominio.com' # Endereço de e-mail de envio