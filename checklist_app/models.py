# checklist_app/models.py

from datetime import datetime
from app import db # Importamos a instância `db` que criamos em `app.py`
from flask_login import UserMixin # Importamos o UserMixin

# Tabela auxiliar para a relação entre Avaliadores e Colaboradores
avaliador_colaborador = db.Table('avaliador_colaborador',
    db.Column('avaliador_id', db.Integer, db.ForeignKey('usuario.id'), primary_key=True),
    db.Column('colaborador_id', db.Integer, db.ForeignKey('colaborador.id'), primary_key=True)
)

class Usuario(db.Model, UserMixin):
    __tablename__ = 'usuario'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    login = db.Column(db.String(50), unique=True, nullable=False)
    senha = db.Column(db.String(128), nullable=False) # Armazenaremos o hash da senha
    perfil = db.Column(db.String(20), nullable=False, default='colaborador') # 'administrador', 'coordenador', 'lider', 'avaliador', 'colaborador'

    def __repr__(self):
        return f"Usuário('{self.nome}', '{self.login}', '{self.perfil}')"

# Crie uma função de user_loader para o Flask-Login
from app import login_manager

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

class Setor(db.Model):
    __tablename__ = 'setor'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), unique=True, nullable=False)

    def __repr__(self):
        return f"Setor('{self.nome}')"

class Colaborador(db.Model):
    __tablename__ = 'colaborador'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    data_inicio = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    status = db.Column(db.String(20), nullable=False, default='em_treinamento') # 'em_treinamento', 'aprovado', 'reprovado'

    # Relacionamentos com as outras tabelas
    setor_id = db.Column(db.Integer, db.ForeignKey('setor.id'), nullable=False)
    lider_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)

    # Relacionamento M-M para avaliadores
    avaliadores = db.relationship('Usuario', secondary=avaliador_colaborador, lazy='subquery',
                                  backref=db.backref('colaboradores_avaliados', lazy=True))

    def __repr__(self):
        return f"Colaborador('{self.nome}', '{self.status}')"

class ChecklistModelo(db.Model):
    __tablename__ = 'checklist_modelo'
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(20), nullable=False) # 'diario' ou 'semanal'
    itens = db.Column(db.JSON, nullable=False) # Armazenaremos a lista de itens como um objeto JSON

    def __repr__(self):
        return f"ChecklistModelo('{self.tipo}')"

class ChecklistRespostas(db.Model):
    __tablename__ = 'checklist_respostas'
    id = db.Column(db.Integer, primary_key=True)
    data_preenchimento = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    observacoes = db.Column(db.Text)
    assinaturas = db.Column(db.JSON)
    respostas = db.Column(db.JSON)
    pontuacao_final = db.Column(db.Integer) # Nova coluna para a pontuação
    situacao = db.Column(db.String(20)) # Nova coluna para a situação: 'Aprovado' ou 'Reprovado'

    # Relacionamentos
    colaborador_id = db.Column(db.Integer, db.ForeignKey('colaborador.id'), nullable=False)
    modelo_id = db.Column(db.Integer, db.ForeignKey('checklist_modelo.id'), nullable=False)

    def __repr__(self):
        return f"ChecklistRespostas('{self.colaborador_id}', '{self.data_preenchimento}')"