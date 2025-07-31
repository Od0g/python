# routes.py
from flask import render_template, request, redirect, url_for, flash, send_file, abort
from app import app, db
from models import ChecklistTemplate, Checklist, ChecklistItemTemplate, ChecklistAnswer, User, Role, ValidationLog
from flask_login import login_user, current_user, logout_user, login_required, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import base64
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from PIL import Image
import os
import tempfile
import pandas as pd
from datetime import datetime
from flask_mail import Message, Mail
from app import mail # Importe a instância de mail do app


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
    roles = ['Administrador', 'Avaliador', 'Líder', 'Gestor', 'Qualidade', 'Seguranca', 'Coordenação']
    
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
    checklists = Checklist.query.all()
    return render_template('index.html', checklists=checklists)

@app.route('/modelos/cadastrar', methods=['GET', 'POST'])
@login_required
def cadastrar_modelo():
    # Lógica de autorização: apenas administradores podem criar modelos
    if current_user.role_obj.name != 'Administrador':
        flash('Você não tem permissão para acessar esta página.', 'danger')
        return redirect(url_for('index'))

    if request.method == 'POST':
        try:
            nome = request.form.get('nome')
            descricao = request.form.get('descricao')
            setor = request.form.get('setor')
            
            novo_modelo = ChecklistTemplate(name=nome, description=descricao, sector=setor)
            db.session.add(novo_modelo)
            db.session.commit()

            perguntas_text = request.form.getlist('pergunta[]')
            comentarios_obrigatorios = request.form.getlist('comentario_obrigatorio[]')
            
            for i, pergunta_texto in enumerate(perguntas_text):
                requires_comment = 'on' in comentarios_obrigatorios[i] if i < len(comentarios_obrigatorios) else False
                
                novo_item_modelo = ChecklistItemTemplate(
                    template_id=novo_modelo.id,
                    question_number=i + 1,
                    question_text=pergunta_texto,
                    requires_comment_if_no=requires_comment,
                    order_index=i + 1
                )
                db.session.add(novo_item_modelo)

            db.session.commit()
            flash('Modelo de checklist criado com sucesso!', 'success')
            return redirect(url_for('index'))

        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao cadastrar modelo: {e}', 'danger')

    return render_template('cadastrar_modelo.html')


@app.route('/criar_checklist')
@login_required
def selecionar_modelo():
    modelos = ChecklistTemplate.query.filter_by(is_active=True).all()
    return render_template('selecionar_modelo.html', modelos=modelos)

@app.route('/preencher_checklist/<int:modelo_id>', methods=['GET', 'POST'])
@login_required
def preencher_checklist(modelo_id):
    if request.method == 'GET':
        modelo = ChecklistTemplate.query.get_or_404(modelo_id)

        novo_checklist = Checklist(
            template_id=modelo.id,
            created_by_user_id=current_user.id,
            evaluator_user_id=current_user.id,
            evaluated_employee_name="Colaborador",
            employee_matricula="",
            employee_position="",
            shift="",
            area="",
            training_date=datetime.utcnow().date(),
            training_coach="",
            training_load_hours="",
            training_process_desc="",
            start_datetime=datetime.utcnow(),
            current_status='Em Andamento',
            saved_partially=True
        )
        db.session.add(novo_checklist)
        db.session.commit()

        for item_template in modelo.items:
            nova_resposta = ChecklistAnswer(
                checklist_id=novo_checklist.id,
                item_template_id=item_template.id,
                answer='NSP',
                comment=''
            )
            db.session.add(nova_resposta)
        db.session.commit()

        flash('Novo checklist criado com sucesso! Preencha as informações.', 'success')
        return redirect(url_for('editar_checklist', checklist_id=novo_checklist.id))

@app.route('/editar_checklist/<int:checklist_id>', methods=['GET', 'POST'])
@login_required
def editar_checklist(checklist_id):
    checklist = Checklist.query.get_or_404(checklist_id)

    if request.method == 'POST':
        checklist.evaluated_employee_name = request.form.get('evaluated_employee_name')
        checklist.employee_matricula = request.form.get('employee_matricula')
        checklist.employee_position = request.form.get('employee_position')
        checklist.shift = request.form.get('shift')
        checklist.area = request.form.get('area')
        checklist.training_date = datetime.strptime(request.form.get('training_date'), '%Y-%m-%d').date()
        checklist.training_coach = request.form.get('training_coach')
        checklist.training_load_hours = request.form.get('training_load_hours')
        checklist.training_process_desc = request.form.get('training_process_desc')

        for answer in checklist.answers:
            answer.answer = request.form.get(f'answer_{answer.id}', 'NSP')
            answer.comment = request.form.get(f'comment_{answer.id}', '')

        assinatura_data_url = request.form.get('assinatura_avaliador_data')
        if assinatura_data_url:
            header, encoded = assinatura_data_url.split(",", 1)
            checklist.evaluator_signature_data = base64.b64decode(encoded)
            checklist.evaluator_signature_name = request.form.get('avaliador_nome')
            checklist.evaluator_signature_datetime = datetime.utcnow()
        
        checklist.current_status = 'Aguardando Validação'
        checklist.saved_partially = False
        checklist.end_datetime = datetime.utcnow()
        
        db.session.commit()
        
        flash('Checklist preenchido e enviado para validação com sucesso!', 'success')
        return redirect(url_for('index'))

    return render_template('preencher_checklist.html', checklist=checklist)

@app.route('/validar_checklist/<int:checklist_id>', methods=['GET', 'POST'])
@login_required
def validar_checklist(checklist_id):
    checklist = Checklist.query.get_or_404(checklist_id)

    # Verifica se o checklist já foi aprovado por este validador
    if ValidationLog.query.filter_by(checklist_id=checklist.id, validator_user_id=current_user.id).first():
        flash('Você já validou este checklist.', 'warning')
        return redirect(url_for('index'))

    # Lógica de autorização: apenas usuários com perfil de aprovação podem validar.
    perfis_de_validacao = ['Líder', 'Gestor', 'Qualidade', 'Seguranca', 'Coordenação']
    if current_user.role_obj.name not in perfis_de_validacao:
        flash('Você não tem permissão para validar checklists.', 'danger')
        return redirect(url_for('index'))

    # Se a validação for via POST, processa o formulário
    if request.method == 'POST':
        assinatura_data_url = request.form.get('assinatura_validador_data')
        
        if not assinatura_data_url:
            flash('Por favor, assine antes de validar o checklist.', 'danger')
            return redirect(url_for('validar_checklist', checklist_id=checklist.id))

        try:
            header, encoded = assinatura_data_url.split(",", 1)
            
            log = ValidationLog(
                checklist_id=checklist.id,
                validator_user_id=current_user.id,
                validation_status='Aprovado',
                comment=request.form.get('comentario_validador'),
                signature_data=base64.b64decode(encoded),
                signature_name=current_user.username
            )
            db.session.add(log)
            db.session.commit()

            # Atualiza o status do checklist com base na validação
            checklist.current_status = f'Aprovado por {current_user.role_obj.name}'
            # Em um sistema real, você verificaria se todas as validações necessárias foram feitas antes de mudar o status final.
            
            db.session.commit()
            
            flash(f'Checklist aprovado com sucesso por {current_user.role_obj.name}.', 'success')
            return redirect(url_for('index'))

        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao validar checklist: {e}', 'danger')
            return redirect(url_for('validar_checklist', checklist_id=checklist.id))
            
    # Se for GET, exibe o checklist completo para validação
    return render_template('validar_checklist.html', checklist=checklist)

@app.route('/historico')
@login_required
def historico():
    checklists = Checklist.query.order_by(Checklist.created_at.desc()).all()
    return render_template('historico.html', checklists=checklists)

@app.route('/ver_detalhes/<int:checklist_id>')
@login_required
def ver_detalhes(checklist_id):
    checklist = Checklist.query.get_or_404(checklist_id)
    return render_template('ver_detalhes.html', checklist=checklist)

@app.route('/gerar_pdf/<int:checklist_id>')
@login_required
def gerar_pdf(checklist_id):
    checklist = Checklist.query.get_or_404(checklist_id)
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # Adicionando o cabeçalho
    c.setFont("Helvetica-Bold", 14)
    c.drawString(100, height - 50, f"Relatório do Checklist ID: {checklist.id}")
    c.setFont("Helvetica", 12)
    c.drawString(100, height - 70, f"Modelo: {checklist.template.name}")
    c.drawString(100, height - 90, f"Avaliador: {checklist.evaluator.username}")
    c.drawString(100, height - 110, f"Colaborador Avaliado: {checklist.evaluated_employee_name}")
    c.drawString(100, height - 130, f"Status: {checklist.current_status}")

    # Adicionando os itens do checklist
    y_pos = height - 170
    c.setFont("Helvetica-Bold", 12)
    c.drawString(100, y_pos, "Itens do Checklist:")
    y_pos -= 20
    c.setFont("Helvetica", 10)
    for answer in checklist.answers:
        c.drawString(100, y_pos, f"Pergunta: {answer.item_template.question_text}")
        y_pos -= 12
        c.drawString(120, y_pos, f"Resposta: {answer.answer}")
        y_pos -= 12
        c.drawString(120, y_pos, f"Comentário: {answer.comment or 'N/A'}")
        y_pos -= 20
        if y_pos < 50:
            c.showPage()
            y_pos = height - 50
            c.setFont("Helvetica", 10)

    # Adicionando assinatura do avaliador
    y_pos -= 20
    if checklist.evaluator_signature_data:
        c.setFont("Helvetica-Bold", 12)
        c.drawString(100, y_pos, "Assinatura do Avaliador:")
        y_pos -= 15
        try:
            # LÓGICA CORRIGIDA AQUI
            img_pil = Image.open(BytesIO(checklist.evaluator_signature_data))
            if img_pil.mode in ('RGBA', 'LA'):
                background = Image.new("RGB", img_pil.size, (255, 255, 255))
                background.paste(img_pil, (0, 0), img_pil)
                img_pil = background

            with tempfile.NamedTemporaryFile(delete=True, suffix='.png') as temp_file:
                img_pil.save(temp_file, format='PNG')
                temp_file.flush()
                c.drawImage(temp_file.name, 100, y_pos - 80, width=200, height=80)
            c.setFont("Helvetica", 10)
            c.drawString(100, y_pos - 90, f"Nome: {checklist.evaluator_signature_name}")
            c.drawString(100, y_pos - 100, f"Data: {checklist.evaluator_signature_datetime.strftime('%d/%m/%Y %H:%M')}")
        except Exception as e:
            c.drawString(100, y_pos - 100, f"Erro ao carregar assinatura do avaliador: {e}")
        y_pos -= 120
    
    # Adicionando logs de validação
    if checklist.validation_logs:
        c.showPage()
        y_pos = height - 50
        c.setFont("Helvetica-Bold", 14)
        c.drawString(100, y_pos, "Histórico de Validações:")
        y_pos -= 30
        c.setFont("Helvetica", 10)
        for log in checklist.validation_logs:
            c.setFont("Helvetica-Bold", 12)
            c.drawString(100, y_pos, f"Validador: {log.validator.username} ({log.validator.role_obj.name})")
            y_pos -= 15
            c.setFont("Helvetica", 10)
            c.drawString(120, y_pos, f"Status: {log.validation_status}")
            y_pos -= 12
            c.drawString(120, y_pos, f"Comentário: {log.comment or 'N/A'}")
            y_pos -= 15
            if log.signature_data:
                try:
                    # LÓGICA CORRIGIDA AQUI
                    img_pil_log = Image.open(BytesIO(log.signature_data))
                    if img_pil_log.mode in ('RGBA', 'LA'):
                        background = Image.new("RGB", img_pil_log.size, (255, 255, 255))
                        background.paste(img_pil_log, (0, 0), img_pil_log)
                        img_pil_log = background
                    
                    with tempfile.NamedTemporaryFile(delete=True, suffix='.png') as temp_file:
                        img_pil_log.save(temp_file, format='PNG')
                        temp_file.flush()
                        c.drawImage(temp_file.name, 120, y_pos - 80, width=150, height=60)
                except Exception as e:
                    c.drawString(120, y_pos - 80, f"Erro ao carregar assinatura: {e}")
                y_pos -= 100
            c.drawString(120, y_pos, f"Data: {log.validation_datetime.strftime('%d/%m/%Y %H:%M')}")
            y_pos -= 30
            if y_pos < 50:
                c.showPage()
                y_pos = height - 50

    c.save()
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name=f"checklist_{checklist_id}.pdf", mimetype='application/pdf')

@app.route('/gerar_excel/<int:checklist_id>')
@login_required
def gerar_excel(checklist_id):
    checklist = Checklist.query.get_or_404(checklist_id)
    data = []

    base_data = {
        "ID do Checklist": checklist.id,
        "Modelo": checklist.template.name,
        "Avaliador": checklist.evaluator.username,
        "Colaborador Avaliado": checklist.evaluated_employee_name,
        "Matrícula": checklist.employee_matricula,
        "Cargo": checklist.employee_position,
        "Turno": checklist.shift,
        "Área": checklist.area,
        "Data de Treinamento": checklist.training_date.strftime('%Y-%m-%d') if checklist.training_date else 'N/A',
        "Treinador": checklist.training_coach,
        "Carga Horária": checklist.training_load_hours,
        "Processo de Treinamento": checklist.training_process_desc,
        "Status": checklist.current_status,
        "Assinatura Avaliador": checklist.evaluator_signature_name,
        "Data Assinatura": checklist.evaluator_signature_datetime.strftime('%d/%m/%Y %H:%M') if checklist.evaluator_signature_datetime else 'N/A',
    }

    # Adiciona os dados de validação
    for i, log in enumerate(checklist.validation_logs):
        base_data[f"Validador_{i+1}"] = log.validator.username
        base_data[f"Status_Validacao_{i+1}"] = log.validation_status
        base_data[f"Comentario_Validacao_{i+1}"] = log.comment or 'N/A'
        base_data[f"Data_Validacao_{i+1}"] = log.validation_datetime.strftime('%d/%m/%Y %H:%M') if log.validation_datetime else 'N/A'
        base_data[f"Assinatura_Validacao_{i+1}"] = log.signature_name or 'N/A'

    # Adiciona as respostas
    if checklist.answers:
        for answer in checklist.answers:
            row = base_data.copy()
            row["Pergunta"] = answer.item_template.question_text
            row["Resposta"] = answer.answer
            row["Comentário"] = answer.comment or 'N/A'
            data.append(row)
    else:
        data.append(base_data)

    # Criação do Excel
    df = pd.DataFrame(data)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Checklist Data')
    output.seek(0)

    return send_file(
        output,
        as_attachment=True,
        download_name=f"checklist_{checklist_id}.xlsx",
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

@app.route('/enviar_email/<int:checklist_id>', methods=['GET', 'POST'])
@login_required
def enviar_email(checklist_id):
    checklist = Checklist.query.get_or_404(checklist_id)

    # Lógica para gerar o PDF em memória (reutilizando a lógica do gerar_pdf)
    buffer = BytesIO()
    # ... (toda a lógica para gerar o PDF que está na sua função gerar_pdf) ...
    # No seu código, você pode extrair a lógica de geração de PDF para uma função separada para evitar duplicação.
    
    # Por enquanto, vamos simplificar a lógica de geração de PDF para este exemplo
    c = canvas.Canvas(buffer, pagesize=letter)
    c.drawString(100, 100, "Conteúdo do PDF do Checklist.")
    c.save()
    buffer.seek(0)
    
    if request.method == 'POST':
        destinatario = request.form.get('destinatario')
        assunto = f"Checklist #{checklist.id} - Relatório de Validação"
        
        msg = Message(
            subject=assunto,
            recipients=[destinatario],
            body="Segue o relatório do checklist em anexo."
        )
        
        # Anexa o PDF ao e-mail
        msg.attach(
            f"checklist_{checklist.id}.pdf",
            "application/pdf",
            buffer.getvalue()
        )
        
        try:
            mail.send(msg)
            flash('E-mail enviado com sucesso!', 'success')
            return redirect(url_for('ver_detalhes', checklist_id=checklist.id))
        except Exception as e:
            flash(f'Erro ao enviar e-mail: {e}', 'danger')
            return redirect(url_for('ver_detalhes', checklist_id=checklist.id))

    return render_template('enviar_email.html', checklist=checklist)

@app.route('/admin')
@login_required
def admin_panel():
    if current_user.role_obj.name != 'Administrador':
        flash('Você não tem permissão para acessar esta página.', 'danger')
        return redirect(url_for('index'))
    return render_template('admin.html')


@app.route('/admin/gerenciar_modelos')
@login_required
def gerenciar_modelos():
    if current_user.role_obj.name != 'Administrador':
        flash('Você não tem permissão para acessar esta página.', 'danger')
        return redirect(url_for('index'))
    
    modelos = ChecklistTemplate.query.all()
    return render_template('gerenciar_modelos.html', modelos=modelos)


@app.route('/admin/toggle_modelo/<int:modelo_id>')
@login_required
def toggle_modelo(modelo_id):
    if current_user.role_obj.name != 'Administrador':
        flash('Você não tem permissão para realizar esta ação.', 'danger')
        return redirect(url_for('index'))
    
    modelo = ChecklistTemplate.query.get_or_404(modelo_id)
    modelo.is_active = not modelo.is_active
    db.session.commit()
    
    flash(f"O modelo '{modelo.name}' foi {'ativado' if modelo.is_active else 'desativado'}.", 'success')
    return redirect(url_for('gerenciar_modelos'))