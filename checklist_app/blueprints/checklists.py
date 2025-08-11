# checklist_app/blueprints/checklists.py

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import Colaborador, ChecklistModelo, ChecklistRespostas, Setor
from app import db
import json
from datetime import datetime

checklists = Blueprint('checklists', __name__, template_folder='../templates/checklists')

@checklists.route('/preencher_checklist/<int:colaborador_id>/<string:tipo>', methods=['GET', 'POST'])
@login_required
def preencher_checklist(colaborador_id, tipo):
    colaborador = Colaborador.query.get_or_404(colaborador_id)

    # Verifica se o usuário tem permissão para preencher o checklist
    if current_user.perfil not in ['administrador', 'coordenador', 'lider', 'avaliador']:
        flash('Você não tem permissão para preencher checklists.', 'danger')
        return redirect(url_for('main.dashboard'))

    # Pega o modelo de checklist mais recente
    modelo = ChecklistModelo.query.filter_by(tipo=tipo).order_by(ChecklistModelo.id.desc()).first()
    if not modelo:
        flash(f'Nenhum modelo de checklist "{tipo}" encontrado.', 'danger')
        return redirect(url_for('main.dashboard'))
        
    itens = json.loads(modelo.itens)

    if request.method == 'POST':
        # Lógica para salvar as respostas do checklist
        respostas = {}
        pontuacao_final = 0
        situacao = None
        
        for item in itens:
            resposta_valor = request.form.get(item)
            respostas[item] = resposta_valor
            
            # Lógica de pontuação para checklists semanais
            if tipo == 'semanal' and resposta_valor:
                pontuacao_final += int(resposta_valor)

        # Determinar a situação de aprovação
        if tipo == 'semanal':
            # Definimos uma pontuação mínima para aprovação (ex: 8 de 12)
            pontuacao_minima = 8
            if pontuacao_final >= pontuacao_minima:
                situacao = 'Aprovado'
            else:
                situacao = 'Reprovado'
        
        # Pega a assinatura do formulário
        assinatura_base64 = request.form.get('assinatura_digital')

        nova_resposta = ChecklistRespostas(
            colaborador_id=colaborador.id,
            modelo_id=modelo.id,
            data_preenchimento=datetime.utcnow(),
            observacoes=request.form.get('observacoes'),
            respostas=json.dumps(respostas),
            pontuacao_final=pontuacao_final,
            situacao=situacao,
            assinaturas=json.dumps([assinatura_base64]) # Salva a assinatura como um array JSON
        )
        db.session.add(nova_resposta)
        db.session.commit()
        
        flash(f'Checklist {tipo} de {colaborador.nome} salvo com sucesso! Pontuação: {pontuacao_final} - Situação: {situacao}', 'success')
        return redirect(url_for('main.dashboard'))
    
    return render_template('preencher_checklist.html', 
                           colaborador=colaborador, 
                           tipo=tipo, 
                           itens=itens)

@checklists.route('/historico/<int:colaborador_id>')
@login_required
def historico_checklist(colaborador_id):
    colaborador = Colaborador.query.get_or_404(colaborador_id)
    
    # Busca todas as respostas de checklist para este colaborador
    respostas = ChecklistRespostas.query.filter_by(colaborador_id=colaborador.id).order_by(ChecklistRespostas.data_preenchimento.desc()).all()
    
    return render_template('historico_checklist.html', colaborador=colaborador, respostas=respostas)