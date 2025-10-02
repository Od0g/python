# routes.py
from flask import render_template, request, redirect, url_for, flash, send_file, abort
from app import app, db
from models import (
    ChecklistTemplate, ChecklistInstance, ChecklistItemTemplate, ChecklistAnswer, 
    User, Role, Sector, Employee
)
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
import base64
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from PIL import Image
import os
import tempfile
import pandas as pd
from datetime import datetime, timedelta
import uuid
import re
import binascii

# --- Rotas de Autenticação ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        user = User.query.filter_by(username=request.form.get('username')).first()
        if user and user.check_password(request.form.get('password')):
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Usuário ou senha inválidos!', 'danger')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        role_name = request.form.get('role')
        role = Role.query.filter_by(name=role_name).first()

        if not role:
            flash(f'Perfil "{role_name}" não encontrado. Tente novamente.', 'danger')
            return redirect(url_for('register'))

        user = User(
            username=request.form.get('username'),
            email=request.form.get('email'),
            role_id=role.id
        )
        user.set_password(request.form.get('password'))

        try:
            db.session.add(user)
            db.session.commit()
            flash('Usuário registrado com sucesso! Por favor, faça o login.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao registrar usuário: {e}', 'danger')
            return redirect(url_for('register'))

    roles = Role.query.all()
    return render_template('register.html', roles=roles)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/seed_roles')
def seed_roles():
    roles = ['Administrador', 'Avaliador', 'Líder', 'Gestor', 'Qualidade', 'Seguranca', 'Coordenação', 'Colaborador']
    
    for role_name in roles:
        if not Role.query.filter_by(name=role_name).first():
            role = Role(name=role_name)
            db.session.add(role)
    db.session.commit()
    flash('Perfis de usuário populados com sucesso!', 'success')
    return redirect(url_for('login'))


# --- Rotas Principais do Sistema ---
@app.route('/')
@login_required
def index():
    checklists = ChecklistInstance.query.order_by(ChecklistInstance.created_at.desc()).all()
    return render_template('index.html', checklists=checklists)

@app.route('/admin')
@login_required
def admin_panel():
    if current_user.role_obj.name != 'Administrador':
        flash('Você não tem permissão para acessar esta página.', 'danger')
        return redirect(url_for('index'))
    return render_template('admin/admin.html')

@app.route('/admin/cadastrar_modelo', methods=['GET', 'POST'])
@login_required
def cadastrar_modelo():
    if current_user.role_obj.name != 'Administrador':
        flash('Você não tem permissão para acessar esta página.', 'danger')
        return redirect(url_for('index'))

    if request.method == 'POST':
        try:
            nome = request.form.get('nome')
            checklist_type = request.form.get('checklist_type')
            
            novo_modelo = ChecklistTemplate(name=nome, checklist_type=checklist_type)
            db.session.add(novo_modelo)
            db.session.commit()

            perguntas_text = request.form.getlist('pergunta[]')
            
            for i, pergunta_texto in enumerate(perguntas_text):
                is_score_item = (checklist_type == 'semanal')
                score_block = request.form.getlist('score_block[]')[i] if is_score_item else None
                requires_comment_if_not_ok = 'on' in request.form.getlist('comentario_obrigatorio[]')[i] if not is_score_item else False

                novo_item_modelo = ChecklistItemTemplate(
                    template_id=novo_modelo.id,
                    question_text=pergunta_texto,
                    is_score_item=is_score_item,
                    score_block=score_block,
                    requires_comment_if_not_ok=requires_comment_if_not_ok
                )
                db.session.add(novo_item_modelo)

            db.session.commit()
            flash('Modelo de checklist criado com sucesso!', 'success')
            return redirect(url_for('admin_panel'))

        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao cadastrar modelo: {e}', 'danger')

    return render_template('admin/cadastrar_modelo.html')

@app.route('/admin/cadastrar_setor', methods=['GET', 'POST'])
@login_required
def cadastrar_setor():
    if current_user.role_obj.name != 'Administrador':
        flash('Você não tem permissão para acessar esta página.', 'danger')
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        nome_setor = request.form.get('nome_setor')
        if nome_setor:
            novo_setor = Sector(name=nome_setor)
            db.session.add(novo_setor)
            db.session.commit()
            flash('Setor cadastrado com sucesso!', 'success')
            return redirect(url_for('cadastrar_setor'))
        flash('Nome do setor não pode ser vazio.', 'danger')
    setores = Sector.query.all()
    return render_template('admin/cadastrar_setor.html', setores=setores)


@app.route('/admin/cadastrar_colaborador', methods=['GET', 'POST'])
@login_required
def cadastrar_colaborador():
    if current_user.role_obj.name != 'Administrador':
        flash('Você não tem permissão para acessar esta página.', 'danger')
        return redirect(url_for('index'))

    if request.method == 'POST':
        try:
            nome = request.form.get('nome')
            cargo = request.form.get('cargo')
            matricula = request.form.get('matricula')
            setor_id = request.form.get('setor')
            
            leader_id = request.form.get('leader')
            evaluator_id = request.form.get('evaluator')
            training_start_date_str = request.form.get('training_start_date')
            training_start_date = datetime.strptime(training_start_date_str, '%Y-%m-%d').date()

            novo_colaborador = Employee(
                name=nome,
                position=cargo,
                matricula=matricula,
                sector_id=setor_id,
                start_date=training_start_date
            )
            db.session.add(novo_colaborador)
            db.session.commit()
            
            diario_template = ChecklistTemplate.query.filter_by(checklist_type='diario').first()
            semanal_template = ChecklistTemplate.query.filter_by(checklist_type='semanal').first()
            
            if not diario_template or not semanal_template:
                flash('Modelos de checklist (Diário ou Semanal) não encontrados. Por favor, cadastre-os primeiro.', 'danger')
                return redirect(url_for('cadastrar_colaborador'))

            for i in range(1, 31):
                fill_date = training_start_date + timedelta(days=i-1)
                novo_checklist_diario = ChecklistInstance(
                    checklist_number=str(uuid.uuid4()),
                    template_id=diario_template.id,
                    employee_id=novo_colaborador.id,
                    leader_id=leader_id,
                    evaluator_id=evaluator_id,
                    fill_date=fill_date,
                    day_number=i,
                    week_number=(i-1)//7 + 1,
                    status='Em Andamento'
                )
                db.session.add(novo_checklist_diario)
            
            for i in range(1, 5):
                fill_date = training_start_date + timedelta(weeks=i-1)
                novo_checklist_semanal = ChecklistInstance(
                    checklist_number=str(uuid.uuid4()),
                    template_id=semanal_template.id,
                    employee_id=novo_colaborador.id,
                    leader_id=leader_id,
                    evaluator_id=evaluator_id,
                    fill_date=fill_date,
                    week_number=i,
                    day_number=None,
                    status='Em Andamento'
                )
                db.session.add(novo_checklist_semanal)

            db.session.commit()
            
            flash('Colaborador e agenda de checklists cadastrados com sucesso!', 'success')
            return redirect(url_for('admin_panel'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao cadastrar colaborador: {e}', 'danger')
            
    setores = Sector.query.all()
    lideres = User.query.filter(User.role_obj.has(name='Líder')).all()
    avaliadores = User.query.filter(User.role_obj.has(name='Avaliador')).all()

    return render_template('admin/cadastrar_colaborador.html', setores=setores, lideres=lideres, avaliadores=avaliadores)


@app.route('/historico')
@login_required
def historico():
    checklists = ChecklistInstance.query.order_by(ChecklistInstance.created_at.desc()).all()
    return render_template('historico.html', checklists=checklists)

@app.route('/criar_checklist')
@login_required
def selecionar_modelo():
    modelos = ChecklistTemplate.query.filter_by(is_active=True).all()
    colaboradores = Employee.query.all()
    lideres = User.query.filter(User.role_obj.has(name='Líder')).all()
    avaliadores = User.query.filter(User.role_obj.has(name='Avaliador')).all()
    
    return render_template(
        'selecionar_modelo.html',
        modelos=modelos,
        colaboradores=colaboradores,
        lideres=lideres,
        avaliadores=avaliadores
    )

@app.route('/iniciar_preenchimento', methods=['POST'])
@login_required
def iniciar_preenchimento():
    try:
        modelo_id = request.form.get('modelo_id')
        colaborador_id = request.form.get('colaborador_id')
        leader_id = request.form.get('leader_id')
        evaluator_id = request.form.get('evaluator_id')
        
        modelo = ChecklistTemplate.query.get_or_404(modelo_id)
        colaborador = Employee.query.get_or_404(colaborador_id)
        
        nova_instancia = ChecklistInstance(
            checklist_number=str(uuid.uuid4()),
            template_id=modelo.id,
            employee_id=colaborador.id,
            leader_id=leader_id,
            evaluator_id=evaluator_id,
            fill_date=datetime.utcnow().date(),
            status='Em Andamento'
        )
        db.session.add(nova_instancia)
        db.session.commit()
        
        for item_template in modelo.items:
            nova_resposta = ChecklistAnswer(
                instance_id=nova_instancia.id,
                item_id=item_template.id,
                answer='NSP',
                comment=''
            )
            db.session.add(nova_resposta)
        db.session.commit()
        
        flash('Checklist iniciado com sucesso!', 'success')
        return redirect(url_for('preencher_checklist', instance_id=nova_instancia.id))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao iniciar o checklist: {e}', 'danger')
        return redirect(url_for('selecionar_modelo'))


@app.route('/preencher_checklist/<int:instance_id>', methods=['GET', 'POST'])
@login_required
def preencher_checklist(instance_id):
    checklist = ChecklistInstance.query.get_or_404(instance_id)

    if request.method == 'GET':
        perguntas = ChecklistItemTemplate.query.filter_by(template_id=checklist.template_id).order_by(ChecklistItemTemplate.id).all()
        respostas = {r.item_id: r for r in ChecklistAnswer.query.filter_by(instance_id=checklist.id).all()}
        
        return render_template(
            'preencher_checklist.html',
            checklist=checklist,
            perguntas=perguntas,
            respostas=respostas
        )

    if request.method == 'POST':
        try:
            for item in checklist.template.items:
                answer_key = f'resposta_{item.id}'
                comment_key = f'comentario_{item.id}'
                
                resposta_db = ChecklistAnswer.query.filter_by(
                    instance_id=checklist.id,
                    item_id=item.id
                ).first()
                
                if resposta_db:
                    resposta_db.answer = request.form.get(answer_key)
                    resposta_db.comment = request.form.get(comment_key)
                else:
                    nova_resposta = ChecklistAnswer(
                        instance_id=checklist.id,
                        item_id=item.id,
                        answer=request.form.get(answer_key),
                        comment=request.form.get(comment_key)
                    )
                    db.session.add(nova_resposta)

            assinatura_lider_data = request.form.get('assinatura_lider_data')
            if assinatura_lider_data and 'data:image' in assinatura_lider_data:
                try:
                    header, encoded = assinatura_lider_data.split(",", 1)
                    missing_padding = len(encoded) % 4
                    if missing_padding:
                        encoded += '=' * (4 - missing_padding)
                    checklist.signature_leader_data = base64.b64decode(encoded)
                except (ValueError, binascii.Error) as e:
                    flash(f"Erro ao decodificar a assinatura do Líder: {e}", 'danger')
                    checklist.signature_leader_data = None
            else:
                checklist.signature_leader_data = None

            assinatura_avaliador_data = request.form.get('assinatura_avaliador_data')
            if assinatura_avaliador_data and 'data:image' in assinatura_avaliador_data:
                try:
                    header, encoded = assinatura_avaliador_data.split(",", 1)
                    missing_padding = len(encoded) % 4
                    if missing_padding:
                        encoded += '=' * (4 - missing_padding)
                    checklist.signature_evaluator_data = base64.b64decode(encoded)
                except (ValueError, binascii.Error) as e:
                    flash(f"Erro ao decodificar a assinatura do Avaliador: {e}", 'danger')
                    checklist.signature_evaluator_data = None
            else:
                checklist.signature_evaluator_data = None

            assinatura_colaborador_data = request.form.get('assinatura_colaborador_data')
            if assinatura_colaborador_data and 'data:image' in assinatura_colaborador_data:
                try:
                    header, encoded = assinatura_colaborador_data.split(",", 1)
                    missing_padding = len(encoded) % 4
                    if missing_padding:
                        encoded += '=' * (4 - missing_padding)
                    checklist.signature_employee_data = base64.b64decode(encoded)
                except (ValueError, binascii.Error) as e:
                    flash(f"Erro ao decodificar a assinatura do Colaborador: {e}", 'danger')
                    checklist.signature_employee_data = None
            else:
                checklist.signature_employee_data = None

            checklist.status = 'Concluído'
            db.session.commit()
            
            flash('Checklist preenchido e salvo com sucesso!', 'success')
            return redirect(url_for('index'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao salvar o checklist: {e}', 'danger')
            return redirect(url_for('preencher_checklist', instance_id=instance_id))


@app.route('/ver_detalhes/<int:instance_id>')
@login_required
def ver_detalhes(instance_id):
    checklist = ChecklistInstance.query.get_or_404(instance_id)
    perguntas = ChecklistItemTemplate.query.filter_by(template_id=checklist.template_id).all()
    respostas = {r.item_id: r for r in ChecklistAnswer.query.filter_by(instance_id=checklist.id).all()}
    return render_template(
        'ver_detalhes.html',
        checklist=checklist,
        perguntas=perguntas,
        respostas=respostas
    )

@app.route('/validar_checklist/<int:instance_id>', methods=['GET', 'POST'])
@login_required
def validar_checklist(instance_id):
    checklist = ChecklistInstance.query.get_or_404(instance_id)

    # Verifica se o checklist já foi validado
    if checklist.status in ['Aprovado', 'Reprovado']:
        flash('Este checklist já foi validado.', 'warning')
        return redirect(url_for('ver_detalhes', instance_id=instance_id))

    # Verifica se o usuário logado tem o perfil de Coordenação ou Administrador
    if current_user.role_obj.name not in ['Coordenação', 'Administrador']:
        flash('Você não tem permissão para validar este checklist.', 'danger')
        return redirect(url_for('index'))
    
    if request.method == 'GET':
        perguntas = ChecklistItemTemplate.query.filter_by(template_id=checklist.template_id).all()
        respostas = {r.item_id: r for r in ChecklistAnswer.query.filter_by(instance_id=checklist.id).all()}

        return render_template(
            'validar_checklist.html', 
            checklist=checklist,
            perguntas=perguntas,
            respostas=respostas
        )
    
    if request.method == 'POST':
        try:
            status_final = request.form.get('status_final')
            comentario_coordenador = request.form.get('comentario_coordenador')
            
            assinatura_data = request.form.get('assinatura_coordenador_data')
            if not assinatura_data or 'data:image' not in assinatura_data:
                flash('Assinatura do coordenador é obrigatória para a validação.', 'danger')
                return redirect(url_for('validar_checklist', instance_id=instance_id))

            header, encoded = assinatura_data.split(",", 1)
            missing_padding = len(encoded) % 4
            if missing_padding:
                encoded += '=' * (4 - missing_padding)
            
            checklist.signature_coordinator_data = base64.b64decode(encoded)
            checklist.coordinator_comment = comentario_coordenador
            checklist.status = status_final
            
            db.session.commit()

            flash(f'Checklist validado com sucesso! Status final: {status_final}.', 'success')
            return redirect(url_for('ver_detalhes', instance_id=instance_id))

        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao validar o checklist: {e}', 'danger')
            return redirect(url_for('validar_checklist', instance_id=instance_id))

@app.route('/gerar_pdf/<int:instance_id>')
@login_required
def gerar_pdf(instance_id):
    checklist = ChecklistInstance.query.get_or_404(instance_id)
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    y = height - 50

    c.setFont('Helvetica-Bold', 14)
    c.drawString(100, y, f"Checklist ID: {checklist.id}")
    y -= 20
    c.setFont('Helvetica', 12)
    c.drawString(100, y, f"Modelo: {checklist.template.name}")
    y -= 20
    c.drawString(100, y, f"Colaborador: {checklist.employee.name}")
    y -= 20
    c.drawString(100, y, f"Líder: {checklist.leader.username}")
    y -= 20
    c.drawString(100, y, f"Avaliador: {checklist.evaluator.username}")
    y -= 20
    c.drawString(100, y, f"Status: {checklist.status}")
    y -= 30

    c.setFont('Helvetica-Bold', 12)
    c.drawString(100, y, "Detalhes do Preenchimento:")
    y -= 20
    
    c.setFont('Helvetica', 10)
    for item in checklist.template.items:
        resposta = ChecklistAnswer.query.filter_by(
            instance_id=checklist.id,
            item_id=item.id
        ).first()
        
        if y < 100:
            c.showPage()
            y = height - 50
        
        c.drawString(110, y, f"Pergunta: {item.question_text}")
        y -= 15
        if resposta:
            c.drawString(120, y, f"Resposta: {resposta.answer}")
            y -= 15
            c.drawString(120, y, f"Comentário: {resposta.comment}")
            y -= 25

    c.save()
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name=f"checklist_{checklist.id}.pdf", mimetype='application/pdf')

@app.route('/gerar_excel/<int:instance_id>')
@login_required
def gerar_excel(instance_id):
    checklist = ChecklistInstance.query.get_or_404(instance_id)

    data = []
    for item in checklist.template.items:
        resposta = ChecklistAnswer.query.filter_by(
            instance_id=checklist.id,
            item_id=item.id
        ).first()

        data.append({
            "Checklist ID": checklist.id,
            "Colaborador": checklist.employee.name,
            "Modelo": checklist.template.name,
            "Data de Preenchimento": checklist.fill_date,
            "Pergunta": item.question_text,
            "Resposta": resposta.answer if resposta else "N/A",
            "Comentário": resposta.comment if resposta else "N/A",
            "Status": checklist.status
        })

    df = pd.DataFrame(data)
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Checklist')
    writer.close()
    output.seek(0)

    return send_file(
        output,
        as_attachment=True,
        download_name=f'checklist_{checklist.id}.xlsx',
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )