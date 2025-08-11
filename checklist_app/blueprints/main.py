# checklist_app/blueprints/main.py

from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from models import Colaborador, ChecklistRespostas, Usuario
from app import db
from sqlalchemy import func
from datetime import datetime, timedelta
import models # Adicione esta linha

main = Blueprint('main', __name__)


@main.route('/dashboard')
@login_required
def dashboard():
    # Resumo rápido e lista de colaboradores em risco (código existente)
    colaboradores_em_treinamento = Colaborador.query.filter_by(status='em_treinamento').count()
    # Lógica para encontrar colaboradores com risco de reprovação
    checklists_reprovados = ChecklistRespostas.query.join(models.ChecklistModelo).filter(
        models.ChecklistModelo.tipo == 'semanal',
        ChecklistRespostas.situacao == 'Reprovado'
    ).all()

    # Extrai os colaboradores únicos a partir desses checklists.
    colaboradores_em_risco = set([r.colaborador for r in checklists_reprovados])
    
    # Adicione esta linha para definir a variável total_em_risco
    total_em_risco = len(colaboradores_em_risco)

    # Lógica para os gráficos (CORRIGIDO)
    total_dias_previstos = colaboradores_em_treinamento * 30 if colaboradores_em_treinamento > 0 else 1
    dias_concluidos = ChecklistRespostas.query.join(models.ChecklistModelo).filter(
        models.ChecklistModelo.tipo == 'diario'
    ).count()
    percentual_conclusao = (dias_concluidos / total_dias_previstos) * 100 if total_dias_previstos > 0 else 0
    percentual_pendente = 100 - percentual_conclusao

    # 2. Pontuação média semanal (últimas 4 semanas)
    # A filtragem por tipo deve vir antes do group_by
    pontuacoes_semanais = db.session.query(
        func.avg(ChecklistRespostas.pontuacao_final).label('media'),
        func.strftime('%W', ChecklistRespostas.data_preenchimento).label('semana')
    ).join(models.ChecklistModelo).filter(
        models.ChecklistModelo.tipo == 'semanal'
    ).group_by('semana').order_by('semana').limit(4).all()

    labels_pontuacoes = [f'Semana {p.semana}' for p in pontuacoes_semanais]
    data_pontuacoes = [round(p.media, 2) for p in pontuacoes_semanais]

    # Lógica para alertas (CORRIGIDO)
    data_hoje = datetime.utcnow().date()
    checklists_hoje = ChecklistRespostas.query.join(models.ChecklistModelo).filter(
        func.date(ChecklistRespostas.data_preenchimento) == data_hoje,
        models.ChecklistModelo.tipo == 'diario'
    ).all()
    colaboradores_com_checklist_hoje = [r.colaborador_id for r in checklists_hoje]

    todos_colaboradores_ids = [c.id for c in Colaborador.query.filter_by(status='em_treinamento').all()]
    checklists_nao_preenchidos = [
        Colaborador.query.get(cid) for cid in set(todos_colaboradores_ids) - set(colaboradores_com_checklist_hoje)
    ]
    
    # 3. Listagem de colaboradores (filtrada por perfil)
    if current_user.perfil in ['administrador', 'coordenador']:
        lista_colaboradores = Colaborador.query.all()
    elif current_user.perfil == 'lider':
        lista_colaboradores = Colaborador.query.filter_by(lider_id=current_user.id).all()
    else: # Colaborador/Avaliador
        lista_colaboradores = [Colaborador.query.get(current_user.id)]

    return render_template('dashboard.html',
                           colaboradores_em_treinamento=colaboradores_em_treinamento,
                           dias_concluidos=dias_concluidos,
                           total_em_risco=total_em_risco,
                           colaboradores_em_risco=colaboradores_em_risco,
                           lista_colaboradores=lista_colaboradores,
                           percentual_conclusao=percentual_conclusao,
                           percentual_pendente=percentual_pendente,
                           labels_pontuacoes=labels_pontuacoes,
                           data_pontuacoes=data_pontuacoes,
                           checklists_nao_preenchidos=checklists_nao_preenchidos)


@main.route('/colaboradores')
@login_required
def listar_colaboradores():
    # Esta rota pode ser uma listagem mais detalhada.
    if current_user.perfil in ['administrador', 'coordenador']:
        colaboradores = Colaborador.query.all()
    elif current_user.perfil == 'lider':
        colaboradores = Colaborador.query.filter_by(lider_id=current_user.id).all()
    else: # Colaborador/Avaliador
        colaboradores = [] # Ou uma query vazia para exibir nada

    return render_template('listar_colaboradores.html', colaboradores=colaboradores)