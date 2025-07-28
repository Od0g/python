# models.py
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class ChecklistTemplate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome_checklist = db.Column(db.String(100), nullable=False)
    itens_json = db.Column(db.JSON)
    checklists = db.relationship('Checklist', backref='template', lazy=True)

class Checklist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    template_id = db.Column(db.Integer, db.ForeignKey('checklist_template.id'), nullable=False)
    data_preenchimento = db.Column(db.Date, nullable=False, default=datetime.utcnow)

    # Novos campos para o contexto de treinamento
    treinador = db.Column(db.String(100), nullable=False)
    carga_horaria = db.Column(db.String(50), nullable=True) # Ex: "8 horas", "4h"
    processo_treinamento = db.Column(db.Text, nullable=True) # Descrição do processo

    # Campos existentes (renomeados para clareza se necessário, ou mantidos)
    avaliador = db.Column(db.String(100), nullable=False) # Pode ser o mesmo que treinador ou diferente
    setor = db.Column(db.String(100), nullable=False)
    turno = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(50), default='Pendente')

    itens = db.relationship('ChecklistItem', backref='checklist', lazy=True)

    # Assinatura do Funcionário
    assinatura_funcionario_data = db.Column(db.LargeBinary, nullable=True) # Imagem da assinatura
    nome_funcionario_assinatura = db.Column(db.String(100), nullable=True)
    data_hora_funcionario_assinatura = db.Column(db.DateTime, nullable=True)

    # Assinatura do Gestor
    assinatura_gestor_data = db.Column(db.LargeBinary, nullable=True) # Imagem da assinatura
    nome_gestor_assinatura = db.Column(db.String(100), nullable=True)
    data_hora_gestor_assinatura = db.Column(db.DateTime, nullable=True)


class ChecklistItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    checklist_id = db.Column(db.Integer, db.ForeignKey('checklist.id'), nullable=False)
    item_nome = db.Column(db.String(200), nullable=False)
    valor_preenchido = db.Column(db.String(100), nullable=True)
    observacoes = db.Column(db.Text, nullable=True)

# A tabela Assinatura original não será mais necessária se as assinaturas forem direto no Checklist
# Se você quiser manter a flexibilidade de múltiplas assinaturas por checklist,
# você pode adaptar a tabela Assinatura para ter um campo 'tipo_assinatura' (e.g., 'funcionario', 'gestor')
# e criar múltiplas entradas para o mesmo checklist_id.
# Por enquanto, removi a tabela Assinatura para simplificar, mas saiba que essa é uma alternativa.