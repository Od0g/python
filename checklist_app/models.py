from app import db, login # Importamos o db e o login do nosso app.py
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
import enum

# Usamos Enum para o campo 'perfil' para garantir que apenas valores válidos sejam inseridos.
class PerfilUsuario(enum.Enum):
    ADMIN = 'admin'
    GESTOR = 'gestor'
    COLABORADOR = 'colaborador'

class RespostaOpcoes(enum.Enum):
    SIM = 'Sim'
    NAO = 'Não'
    PARCIAL = 'Parcial'
    NSP = 'Não se aplica'

class Setor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), index=True, unique=True, nullable=False)
    
    # Relacionamentos
    usuarios = db.relationship('Usuario', back_populates='setor', lazy='dynamic')
    perguntas = db.relationship('Pergunta', back_populates='setor', lazy='dynamic')
    checklists = db.relationship('Checklist', back_populates='setor', lazy='dynamic')

    def __repr__(self):
        return f'<Setor {self.nome}>'

class Usuario(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    senha_hash = db.Column(db.String(128))
    perfil = db.Column(db.Enum(PerfilUsuario), nullable=False, default=PerfilUsuario.COLABORADOR)
    
    setor_id = db.Column(db.Integer, db.ForeignKey('setor.id'))
    
    # Relacionamentos
    setor = db.relationship('Setor', back_populates='usuarios')
    checklists_preenchidos = db.relationship('Checklist', foreign_keys='Checklist.usuario_id', back_populates='colaborador', lazy='dynamic')
    checklists_validados = db.relationship('Checklist', foreign_keys='Checklist.gestor_id', back_populates='gestor_validador', lazy='dynamic')

    def set_senha(self, senha):
        self.senha_hash = generate_password_hash(senha)

    def check_senha(self, senha):
        return check_password_hash(self.senha_hash, senha)

    def __repr__(self):
        return f'<Usuario {self.nome}>'

class Pergunta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    texto = db.Column(db.String(500), nullable=False)
    obrigatoria = db.Column(db.Boolean, default=True, nullable=False)
    
    setor_id = db.Column(db.Integer, db.ForeignKey('setor.id'), nullable=False)
    
    # Relacionamento
    setor = db.relationship('Setor', back_populates='perguntas')

    def __repr__(self):
        return f'<Pergunta {self.id}: {self.texto[:30]}...>'

class Checklist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.Date, nullable=False, index=True)
    assinatura_colaborador = db.Column(db.String(100)) # Armazena o nome/hash para validação
    assinatura_gestor = db.Column(db.String(100))
    
    setor_id = db.Column(db.Integer, db.ForeignKey('setor.id'), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False) # Colaborador
    gestor_id = db.Column(db.Integer, db.ForeignKey('usuario.id')) # Gestor que validou
    
    # Relacionamentos
    setor = db.relationship('Setor', back_populates='checklists')
    colaborador = db.relationship('Usuario', foreign_keys=[usuario_id], back_populates='checklists_preenchidos')
    gestor_validador = db.relationship('Usuario', foreign_keys=[gestor_id], back_populates='checklists_validados')
    respostas = db.relationship('Resposta', back_populates='checklist', lazy='dynamic', cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Checklist ID {self.id} - Setor {self.setor.nome} em {self.data}>'

class Resposta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    resposta = db.Column(db.Enum(RespostaOpcoes), nullable=False)
    comentario = db.Column(db.String(500))
    
    checklist_id = db.Column(db.Integer, db.ForeignKey('checklist.id'), nullable=False)
    pergunta_id = db.Column(db.Integer, db.ForeignKey('pergunta.id'), nullable=False)
    
    # Relacionamentos
    checklist = db.relationship('Checklist', back_populates='respostas')
    pergunta = db.relationship('Pergunta') # Relacionamento simples, não precisa de back_populates aqui

    def __repr__(self):
        return f'<Resposta {self.id} - Pergunta {self.pergunta_id} - Resposta: {self.resposta.value}>'