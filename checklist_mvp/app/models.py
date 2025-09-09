from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

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

# Outros modelos (Checklist, Revisoes, etc.) podem ser adicionados aqui posteriormente.