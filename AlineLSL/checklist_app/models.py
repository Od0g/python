# models.py
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin # Importar UserMixin
import uuid

# Inicializa o SQLAlchemy. O objeto 'db' é o ponto central da nossa interação com o banco de dados.
db = SQLAlchemy()

# ==================================================================================================
# Modelos para Acesso e Estrutura do Sistema
# ==================================================================================================

# Tabela para Perfis de Acesso (Ex: Administrador, Líder, Avaliador)
class Role(db.Model):
    __tablename__ = 'role'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    # Relação para conectar perfis a usuários
    users = db.relationship('User', backref='role_obj', lazy=True)

# Tabela de Usuários do Sistema
class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id', name='fk_user_role'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Métodos para gerenciar senhas com segurança
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    # O Flask-Login agora usará o método get_id() padrão do UserMixin,
    # que já retorna o id. Não precisamos implementá-lo.
    def get_id(self):
        return str(self.id)
    
    def __repr__(self):
        return f"<User '{self.username}'>"

# Tabela para Setores
class Sector(db.Model):
    __tablename__ = 'sector'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    employees = db.relationship('Employee', backref='sector', lazy=True)

# Tabela para Cadastro de Colaboradores (avaliados)
class Employee(db.Model):
    __tablename__ = 'employee'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    position = db.Column(db.String(100), nullable=False)
    sector_id = db.Column(db.Integer, db.ForeignKey('sector.id', name='fk_employee_sector'), nullable=False)
    matricula = db.Column(db.String(50), unique=True, nullable=False)
    start_date = db.Column(db.Date, nullable=False, default=datetime.utcnow().date())
    status = db.Column(db.String(50), default='Ativo')

# ==================================================================================================
# Modelos para Checklists e Respostas
# ==================================================================================================

# Tabela para Modelos de Checklist (Template)
class ChecklistTemplate(db.Model):
    __tablename__ = 'checklist_template'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, unique=True)
    checklist_type = db.Column(db.String(50), nullable=False) # 'diario' ou 'semanal'
    is_active = db.Column(db.Boolean, default=True)
    items = db.relationship('ChecklistItemTemplate', backref='template', lazy=True)

# Tabela para Itens (Perguntas/Notas) de um Modelo
class ChecklistItemTemplate(db.Model):
    __tablename__ = 'checklist_item_template'
    id = db.Column(db.Integer, primary_key=True)
    template_id = db.Column(db.Integer, db.ForeignKey('checklist_template.id', name='fk_item_template'), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    is_score_item = db.Column(db.Boolean, default=False) # Se for item de nota (para checklist semanal)
    score_block = db.Column(db.String(50), nullable=True) # Ex: 'Segurança', 'Qualidade'
    requires_comment_if_not_ok = db.Column(db.Boolean, default=False)

# Tabela para o Checklist Preenchido (instância)
class ChecklistInstance(db.Model):
    __tablename__ = 'checklist_instance'
    id = db.Column(db.Integer, primary_key=True)
    checklist_number = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    template_id = db.Column(db.Integer, db.ForeignKey('checklist_template.id', name='fk_instance_template'), nullable=False)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id', name='fk_instance_employee'), nullable=False)
    leader_id = db.Column(db.Integer, db.ForeignKey('user.id', name='fk_instance_leader'), nullable=False)
    evaluator_id = db.Column(db.Integer, db.ForeignKey('user.id', name='fk_instance_evaluator'), nullable=False)

    template = db.relationship('ChecklistTemplate', backref='instances')
    employee = db.relationship('Employee', backref='checklists')
    leader = db.relationship('User', foreign_keys=[leader_id], backref='leader_checklists')
    evaluator = db.relationship('User', foreign_keys=[evaluator_id], backref='evaluator_checklists')
    
    fill_date = db.Column(db.Date, nullable=False, default=datetime.utcnow().date())
    day_number = db.Column(db.Integer, nullable=True)
    week_number = db.Column(db.Integer, nullable=True)
    
    status = db.Column(db.String(50), default='Em Andamento')
    
    signature_leader_data = db.Column(db.LargeBinary, nullable=True)
    signature_evaluator_data = db.Column(db.LargeBinary, nullable=True)
    signature_employee_data = db.Column(db.LargeBinary, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
# Tabela para as Respostas de um Checklist
class ChecklistAnswer(db.Model):
    __tablename__ = 'checklist_answer'
    id = db.Column(db.Integer, primary_key=True)
    instance_id = db.Column(db.Integer, db.ForeignKey('checklist_instance.id', name='fk_answer_instance'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('checklist_item_template.id', name='fk_answer_item'), nullable=False)
    answer = db.Column(db.String(20), nullable=True) # 'Sim', 'Não', 'Parcial', nota (1, 2, 3)
    comment = db.Column(db.Text, nullable=True)