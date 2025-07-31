# models.py
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin # Importe UserMixin

db = SQLAlchemy()

# Tabela para Perfis de Usuário (Roles)
class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    users = db.relationship('User', backref='role_obj', lazy=True)

    def __repr__(self):
        return f"<Role '{self.name}'>"

# Tabela de Usuários
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id', name='fk_user_role'), nullable=False)  # Named constraint
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    checklists_created = db.relationship('Checklist', foreign_keys='Checklist.created_by_user_id', backref='creator', lazy=True)
    checklists_evaluated = db.relationship('Checklist', foreign_keys='Checklist.evaluator_user_id', backref='evaluator', lazy=True)
    validation_logs = db.relationship('ValidationLog', backref='validator', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User '{self.username}'>"

# Tabela para Modelos de Checklist
class ChecklistTemplate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    sector = db.Column(db.String(100), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    items = db.relationship('ChecklistItemTemplate', backref='template', lazy=True, order_by='ChecklistItemTemplate.order_index')
    checklists = db.relationship('Checklist', backref='template', lazy=True)

    def __repr__(self):
        return f"<ChecklistTemplate '{self.name}'>"

# Tabela para Itens (Perguntas) de um Modelo de Checklist
class ChecklistItemTemplate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    template_id = db.Column(db.Integer, db.ForeignKey('checklist_template.id', name='fk_checklist_item_template_template'), nullable=False) # Named constraint
    question_number = db.Column(db.Integer, nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    requires_comment_if_no = db.Column(db.Boolean, default=False)
    order_index = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"<ChecklistItemTemplate '{self.question_text[:50]}...'>"

# Tabela para o Preenchimento de um Checklist (instância)
class Checklist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    template_id = db.Column(db.Integer, db.ForeignKey('checklist_template.id', name='fk_checklist_template'), nullable=False) # Named constraint
    created_by_user_id = db.Column(db.Integer, db.ForeignKey('user.id', name='fk_checklist_creator'), nullable=True) # Named constraint
    evaluator_user_id = db.Column(db.Integer, db.ForeignKey('user.id', name='fk_checklist_evaluator'), nullable=True) # Named constraint

    evaluated_employee_name = db.Column(db.String(100), nullable=False)
    employee_matricula = db.Column(db.String(50), nullable=True)
    employee_position = db.Column(db.String(100), nullable=True)

    shift = db.Column(db.String(50), nullable=False)
    area = db.Column(db.String(100), nullable=False)

    training_date = db.Column(db.Date, nullable=False, default=datetime.utcnow().date())
    training_coach = db.Column(db.String(100), nullable=False)
    training_load_hours = db.Column(db.String(50), nullable=True)
    training_process_desc = db.Column(db.Text, nullable=True)

    start_datetime = db.Column(db.DateTime, nullable=True)
    end_datetime = db.Column(db.DateTime, nullable=True)

    current_status = db.Column(db.String(50), default='Rascunho', nullable=False)
    
    saved_partially = db.Column(db.Boolean, default=True)

    evaluator_signature_data = db.Column(db.LargeBinary, nullable=True)
    evaluator_signature_name = db.Column(db.String(100), nullable=True)
    evaluator_signature_datetime = db.Column(db.DateTime, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    answers = db.relationship('ChecklistAnswer', backref='checklist', lazy=True)
    validation_logs = db.relationship('ValidationLog', backref='checklist', lazy=True)

    def __repr__(self):
        return f"<Checklist {self.id} - {self.template.name}>"

# Tabela para as Respostas de um Item de Checklist
class ChecklistAnswer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    checklist_id = db.Column(db.Integer, db.ForeignKey('checklist.id', name='fk_checklist_answer_checklist'), nullable=False) # Named constraint
    item_template_id = db.Column(db.Integer, db.ForeignKey('checklist_item_template.id', name='fk_checklist_answer_item_template'), nullable=False) # Named constraint
    answer = db.Column(db.String(20), nullable=False)
    comment = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    item_template = db.relationship('ChecklistItemTemplate', backref='answers', lazy=True)

    def __repr__(self):
        return f"<ChecklistAnswer {self.id} for Item {self.item_template_id}>"

# Tabela para o Log de Validações (Líder, Gestor, Qualidade, etc.)
class ValidationLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    checklist_id = db.Column(db.Integer, db.ForeignKey('checklist.id', name='fk_validation_log_checklist'), nullable=False) # Named constraint
    validator_user_id = db.Column(db.Integer, db.ForeignKey('user.id', name='fk_validation_log_validator'), nullable=False) # Named constraint
    validation_status = db.Column(db.String(50), nullable=False)
    comment = db.Column(db.Text, nullable=True)
    validation_datetime = db.Column(db.DateTime, default=datetime.utcnow)
    
    signature_data = db.Column(db.LargeBinary, nullable=True)
    signature_name = db.Column(db.String(100), nullable=True)

    def __repr__(self):
        return f"<ValidationLog {self.id} by {self.validator.username} for Checklist {self.checklist_id}>"