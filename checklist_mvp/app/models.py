from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime



# O UserMixin fornece implementações padrão para os métodos que o Flask-Login espera que as classes de usuário tenham.
class Usuario(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    matricula = db.Column(db.String(64), index=True, unique=True)
    nome = db.Column(db.String(120))
    perfil = db.Column(db.String(64)) # Ex: 'operador', 'lider', 'gestor'
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<Usuario {self.nome}>'

# Função exigida pelo Flask-Login para carregar um usuário a partir do ID da sessão
@login.user_loader
def load_user(id):
    return Usuario.query.get(int(id))

class Ativo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(64), index=True, unique=True)
    descricao = db.Column(db.String(200))
    setor = db.Column(db.String(120))
    
    def __repr__(self):
        return f'<Ativo {self.codigo}>'

class Checklist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    versao = db.Column(db.String(10), default='1.0') # <-- NOVO CAMPO
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    turno = db.Column(db.String(50))
    validado_por_lider = db.Column(db.Boolean, default=False)
    
    # Chaves estrangeiras
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    ativo_id = db.Column(db.Integer, db.ForeignKey('ativo.id'))
    
    # Adicione os backrefs aqui
    usuario = db.relationship('Usuario', backref='checklists')
    ativo = db.relationship('Ativo', backref='checklists')

    # Relacionamentos
    respostas = db.relationship('ChecklistResposta', backref='checklist', lazy='dynamic')

    def __repr__(self):
        return f'<Checklist {self.id}>'

class ItemTemplate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(200), unique=True, nullable=False)
    # Futuramente, podemos adicionar um campo para 'tipo_de_checklist'

    def __repr__(self):
        return f'<ItemTemplate {self.descricao}>'

class ChecklistResposta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(10)) # 'OK' ou 'Falha'
    observacao = db.Column(db.Text)
    foto_path = db.Column(db.String(300)) # Caminho para a imagem salva
    
    # Chaves estrangeiras
    checklist_id = db.Column(db.Integer, db.ForeignKey('checklist.id'))
    item_template_id = db.Column(db.Integer, db.ForeignKey('item_template.id'))
    
    # Relacionamentos
    item_template = db.relationship('ItemTemplate')

    def __repr__(self):
        return f'<ChecklistResposta {self.id} - Status: {self.status}>'