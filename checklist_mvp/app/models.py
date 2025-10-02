# app/models.py - VERSÃO COM MODELOS DE CHECKLIST

from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime

# Tabela de associação Muitos-para-Muitos
# Conecta Modelos de Checklist com Tipos de Ativo
modelo_tipo_ativo_association = db.Table('modelo_tipo_ativo',
    db.Column('modelo_id', db.Integer, db.ForeignKey('modelo_checklist.id'), primary_key=True),
    db.Column('tipo_ativo_id', db.Integer, db.ForeignKey('tipo_ativo.id'), primary_key=True)
)

class Usuario(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    matricula = db.Column(db.String(64), index=True, unique=True)
    nome = db.Column(db.String(120))
    perfil = db.Column(db.String(64))
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    def __repr__(self):
        return f'<Usuario {self.nome}>'

@login.user_loader
def load_user(id):
    return Usuario.query.get(int(id))

# O "Molde" de um checklist, criado pelo Admin
class ModeloChecklist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    descricao = db.Column(db.String(300))
    
    # Relacionamento: um modelo tem muitas perguntas
    itens = db.relationship('ItemModelo', backref='modelo', lazy='dynamic', cascade="all, delete-orphan")

    def __repr__(self):
        return f'<ModeloChecklist {self.nome}>'

# A pergunta/item dentro de um "Molde"
class ItemModelo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pergunta = db.Column(db.String(300), nullable=False)
    # Futuramente: tipo_resposta (OK/Falha, Texto, Número, etc.)
    modelo_id = db.Column(db.Integer, db.ForeignKey('modelo_checklist.id'), nullable=False)

    def __repr__(self):
        return f'<ItemModelo {self.pergunta}>'

# Categoria de Ativo (Ex: Tablet, Pager, Celular)
class TipoAtivo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), unique=True, nullable=False)

    # Relacionamento Muitos-para-Muitos com os modelos de checklist
    modelos_checklist = db.relationship('ModeloChecklist', secondary=modelo_tipo_ativo_association, backref='tipos_ativo')

    def __repr__(self):
        return f'<TipoAtivo {self.nome}>'

# O equipamento físico
class Ativo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(64), index=True, unique=True)
    descricao = db.Column(db.String(200))
    setor = db.Column(db.String(120))
    
    tipo_ativo_id = db.Column(db.Integer, db.ForeignKey('tipo_ativo.id'))
    tipo_ativo = db.relationship('TipoAtivo', backref='ativos')

    def __repr__(self):
        return f'<Ativo {self.codigo}>'

# O checklist preenchido pelo operador
class Checklist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    
    # Chaves estrangeiras
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    ativo_id = db.Column(db.Integer, db.ForeignKey('ativo.id'))
    modelo_id = db.Column(db.Integer, db.ForeignKey('modelo_checklist.id')) # Link para o modelo usado

    # Relacionamentos
    usuario = db.relationship('Usuario', backref='checklists')
    ativo = db.relationship('Ativo', backref='checklists')
    modelo = db.relationship('ModeloChecklist') # Acesso fácil ao modelo
    respostas = db.relationship('ChecklistResposta', backref='checklist', lazy='dynamic', cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Checklist {self.id}>'

# A resposta para uma pergunta de um checklist preenchido
class ChecklistResposta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(10))
    observacao = db.Column(db.Text)
    foto_path = db.Column(db.String(300))
    
    checklist_id = db.Column(db.Integer, db.ForeignKey('checklist.id'))
    item_modelo_id = db.Column(db.Integer, db.ForeignKey('item_modelo.id')) # Link para a pergunta respondida
    
    item_modelo = db.relationship('ItemModelo')

    def __repr__(self):
        return f'<ChecklistResposta {self.id}>'