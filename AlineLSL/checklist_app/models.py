# models.py
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
import uuid

db = SQLAlchemy()

# ==================================================================================================
# Modelos para Acesso e Estrutura do Sistema
# ==================================================================================================

class Role(db.Model):
    __tablename__ = 'role'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    users = db.relationship('User', backref='role_obj', lazy=True)

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id', name='fk_user_role'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Sector(db.Model):
    __tablename__ = 'sector'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    employees = db.relationship('Employee', backref='sector', lazy=True)

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

class ChecklistTemplate(db.Model):
    __tablename__ = 'checklist_template'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, unique=True)
    checklist_type = db.Column(db.String(50), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    items = db.relationship('ChecklistItemTemplate', backref='template', lazy=True)

class ChecklistItemTemplate(db.Model):
    __tablename__ = 'checklist_item_template'
    id = db.Column(db.Integer, primary_key=True)
    template_id = db.Column(db.Integer, db.ForeignKey('checklist_template.id', name='fk_item_template'), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    is_score_item = db.Column(db.Boolean, default=False)
    score_block = db.Column(db.String(50), nullable=True)
    requires_comment_if_not_ok = db.Column(db.Boolean, default=False)

class ChecklistInstance(db.Model):
    __tablename__ = 'checklist_instance'
    id = db.Column(db.Integer, primary_key=True)
    checklist_number = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    template_id = db.Column(db.Integer, db.ForeignKey('checklist_template.id', name='fk_instance_template'), nullable=False)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id', name='fk_instance_employee'), nullable=False)
    leader_id = db.Column(db.Integer, db.ForeignKey('user.id', name='fk_instance_leader'), nullable=False)
    evaluator_id = db.Column(db.Integer, db.ForeignKey('user.id', name='fk_instance_evaluator'), nullable=False)

    template = db.relationship('ChecklistTemplate', backref='instances', lazy=True)
    employee = db.relationship('Employee', backref='checklists', lazy=True)
    leader = db.relationship('User', foreign_keys=[leader_id], backref='leader_checklists', lazy=True)
    evaluator = db.relationship('User', foreign_keys=[evaluator_id], backref='evaluator_checklists', lazy=True)

    fill_date = db.Column(db.Date, nullable=True)
    day_number = db.Column(db.Integer, nullable=True)
    week_number = db.Column(db.Integer, nullable=True)

    status = db.Column(db.String(50), default='Em Andamento')

    signature_leader_data = db.Column(db.LargeBinary, nullable=True)
    signature_evaluator_data = db.Column(db.LargeBinary, nullable=True)
    signature_employee_data = db.Column(db.LargeBinary, nullable=True)

    # Adicione estas duas colunas
    coordinator_comment = db.Column(db.Text, nullable=True)
    signature_coordinator_data = db.Column(db.LargeBinary, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ChecklistAnswer(db.Model):
    __tablename__ = 'checklist_answer'
    id = db.Column(db.Integer, primary_key=True)
    instance_id = db.Column(db.Integer, db.ForeignKey('checklist_instance.id', name='fk_answer_instance'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('checklist_item_template.id', name='fk_answer_item'), nullable=False)
    answer = db.Column(db.String(20), nullable=True)
    comment = db.Column(db.Text, nullable=True)