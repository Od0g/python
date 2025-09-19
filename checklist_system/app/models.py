from app import db, login_manager, bcrypt
from flask_login import UserMixin
# Não precisamos mais destes imports específicos de JSON
# from sqlalchemy.dialects.sqlite import JSON as SQLITE_JSON
# from sqlalchemy.dialects.postgresql import JSONB
# from sqlalchemy.ext.compiler import compiles
# from sqlalchemy.types import TypeDecorator, TEXT
# import json
from datetime import datetime
import enum

# O TIPO DE DADO JSON CUSTOMIZADO FOI REMOVIDO DAQUI

class UserRoles(enum.Enum):
    COLABORADOR = 'Colaborador'
    GESTOR = 'Gestor'
    COORDENADOR = 'Coordenador'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha_hash = db.Column(db.String(128))
    cargo = db.Column(db.Enum(UserRoles), nullable=False, default=UserRoles.COLABORADOR)
    setor_id = db.Column(db.Integer, db.ForeignKey('sector.id'), nullable=False)
    setor = db.relationship('Sector', backref='users')

    def set_password(self, password):
        self.senha_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.senha_hash, password)

class Sector(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), unique=True, nullable=False)

# ---- MODELOS ADICIONADOS PARA PERGUNTAS DINÂMICAS ----
class ChecklistTemplate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), unique=True, nullable=False)
    descricao = db.Column(db.String(300), nullable=True)
    perguntas = db.relationship('Question', backref='template', lazy='dynamic', cascade="all, delete-orphan")

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    texto = db.Column(db.String(500), nullable=False)
    template_id = db.Column(db.Integer, db.ForeignKey('checklist_template.id'), nullable=False)
# ---------------------------------------------------------

class Equipment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    setor_id = db.Column(db.Integer, db.ForeignKey('sector.id'), nullable=False)
    setor = db.relationship('Sector', backref='equipments')
    qr_code = db.Column(db.String(255), nullable=True)
    template_id = db.Column(db.Integer, db.ForeignKey('checklist_template.id'), nullable=True)
    template = db.relationship('ChecklistTemplate', backref='equipments')

class Checklist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    equipamento_id = db.Column(db.Integer, db.ForeignKey('equipment.id'), nullable=False)
    colaborador_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    gestor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    data = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    
    # MUDANÇA CRUCIAL AQUI: Usando o tipo JSON padrão do SQLAlchemy
    respostas = db.Column(db.JSON, nullable=False)
    
    observacoes = db.Column(db.Text, nullable=True)
    assinatura_colaborador = db.Column(db.Text, nullable=False)
    assinatura_gestor = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), default='Pendente')

    equipamento = db.relationship('Equipment', backref='checklists')
    colaborador = db.relationship('User', foreign_keys=[colaborador_id])
    gestor = db.relationship('User', foreign_keys=[gestor_id])

class Alert(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    checklist_id = db.Column(db.Integer, db.ForeignKey('checklist.id'), nullable=False)
    enviado_para = db.Column(db.String(255), nullable=False)
    data_envio = db.Column(db.DateTime, default=datetime.utcnow)
    checklist = db.relationship('Checklist', backref='alerts')