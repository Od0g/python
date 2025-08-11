# checklist_app/config.py

import os

class Config:
    # A chave secreta é usada para segurança.
    # Em produção, você deve usar uma variável de ambiente.
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'sua-chave-secreta-muito-segura'

    # Configuração do banco de dados SQLAlchemy
    SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False