from app import db, login_manager, bcrypt
from flask_login import UserMixin
from sqlalchemy.dialects.sqlite import JSON as SQLITE_JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.types import TypeDecorator, TEXT
import json
from datetime import datetime
import enum

# Workaround para JSON funcionar no SQLite e PostgreSQL
class JSON(TypeDecorator):
    impl = TEXT
    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(JSONB())
        elif dialect.name == 'sqlite':
            return dialect.type_descriptor(SQLITE_JSON())
        else:
            return dialect.type_descriptor(TEXT())
            
    def process_bind_param(self, value, dialect):
        if value is not None:
            return json.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            return json.loads(value)
        return value

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

class Equipment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    setor_id = db.Column(db.Integer, db.ForeignKey('sector.id'), nullable=False)
    setor = db.relationship('Sector', backref='equipments')
    qr_code = db.Column(db.String(255), nullable=True)

class Checklist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    equipamento_id = db.Column(db.Integer, db.ForeignKey('equipment.id'), nullable=False)
    colaborador_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    gestor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    data = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    respostas = db.Column(JSON, nullable=False)
    observacoes = db.Column(db.Text, nullable=True)
    assinatura_colaborador = db.Column(db.Text, nullable=False) # Base64
    assinatura_gestor = db.Column(db.Text, nullable=True) # Base64
    status = db.Column(db.String(50), default='Pendente') # Pendente, Conforme, Não Conforme

    equipamento = db.relationship('Equipment', backref='checklists')
    colaborador = db.relationship('User', foreign_keys=[colaborador_id])
    gestor = db.relationship('User', foreign_keys=[gestor_id])

class Alert(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    checklist_id = db.Column(db.Integer, db.ForeignKey('checklist.id'), nullable=False)
    enviado_para = db.Column(db.String(255), nullable=False)
    data_envio = db.Column(db.DateTime, default=datetime.utcnow)
    checklist = db.relationship('Checklist', backref='alerts')
    