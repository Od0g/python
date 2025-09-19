from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import User, Sector, Equipment, Checklist, UserRoles
from app.forms import UserForm, SectorForm, EquipmentForm
from app.models import ChecklistTemplate, Question # Adicione nos imports
from app.forms import TemplateForm, QuestionForm # Adicione nos imports
from app.email import send_non_compliance_alert
import qrcode
import os
import json
from functools import wraps
from flask import Response
from weasyprint import HTML



bp = Blueprint('main', __name__)

# Decorador para restringir acesso por cargo
def role_required(*roles):
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            if not current_user.is_authenticated or current_user.cargo.name not in roles:
                flash('Você não tem permissão para acessar esta página.', 'danger')
                return redirect(url_for('main.index'))
            return fn(*args, **kwargs)
        return decorated_view
    return wrapper

@bp.route('/')
@login_required
def index():
    # Dados para o Dashboard
    total_checklists = Checklist.query.count()
    conformidade = Checklist.query.filter_by(status='Conforme').count()
    nao_conformidade = Checklist.query.filter_by(status='Não Conforme').count()
    
    percent_conformidade = (conformidade / total_checklists * 100) if total_checklists > 0 else 0
    
    recent_nao_conformes = Checklist.query.filter_by(status='Não Conforme').order_by(Checklist.data.desc()).limit(10).all()

    return render_template('index.html', title='Dashboard', 
                           total=total_checklists,
                           percent_ok=percent_conformidade,
                           total_nok=nao_conformidade,
                           recent_nok=recent_nao_conformes)

# --- ROTAS DE CADASTRO (GESTOR/COORDENADOR) ---

@bp.route('/users', methods=['GET', 'POST'])
@login_required
@role_required('GESTOR', 'COORDENADOR')
def manage_users():
    form = UserForm()
    form.setor.choices = [(s.id, s.nome) for s in Sector.query.order_by('nome').all()]
    if form.validate_on_submit():
        user = User(
            nome=form.nome.data,
            email=form.email.data,
            cargo=UserRoles[form.cargo.data],
            setor_id=form.setor.data
        )
        user.set_password(form.senha.data)
        db.session.add(user)
        db.session.commit()
        flash('Usuário cadastrado com sucesso!', 'success')
        return redirect(url_for('main.manage_users'))
    users = User.query.all()
    return render_template('register_user.html', title='Gerenciar Usuários', form=form, users=users)

@bp.route('/sectors', methods=['GET', 'POST'])
@login_required
@role_required('GESTOR', 'COORDENADOR')
def manage_sectors():
    form = SectorForm()
    if form.validate_on_submit():
        sector = Sector(nome=form.nome.data)
        db.session.add(sector)
        db.session.commit()
        flash('Setor cadastrado com sucesso!', 'success')
        return redirect(url_for('main.manage_sectors'))
    sectors = Sector.query.all()
    return render_template('sectors.html', title='Gerenciar Setores', form=form, sectors=sectors)

@bp.route('/equipment', methods=['GET', 'POST'])
@login_required
@role_required('GESTOR', 'COORDENADOR')
def manage_equipment():
    form = EquipmentForm()
    form.setor.choices = [(s.id, s.nome) for s in Sector.query.order_by('nome').all()]
    # NOVA LINHA PARA POPULAR O DROPDOWN DE MODELOS
    form.template.choices = [(t.id, t.nome) for t in ChecklistTemplate.query.order_by('nome').all()]
    if form.validate_on_submit():
        equip = Equipment(nome=form.nome.data, setor_id=form.setor.data, template_id=form.template.data) # Adicionado template_id
        db.session.add(equip)
        db.session.flush() # Para obter o ID do equipamento antes do commit

        # Gerar QR Code
        qr_code_path = os.path.join(current_app.static_folder, 'qrcodes', f'equip_{equip.id}.png')
        qr_url = url_for('main.fill_checklist', equipment_id=equip.id, _external=True)
        img = qrcode.make(qr_url)
        img.save(qr_code_path)
        
        equip.qr_code = f'qrcodes/equip_{equip.id}.png'
        db.session.commit()
        flash('Equipamento cadastrado e QR Code gerado!', 'success')
        return redirect(url_for('main.manage_equipment'))

    equipments = Equipment.query.all()
    return render_template('equipment.html', title='Gerenciar Equipamentos', form=form, equipments=equipments)

# --- FLUXO DO CHECKLIST ---

@bp.route('/checklist/<int:equipment_id>', methods=['GET', 'POST'])
@login_required
def fill_checklist(equipment_id):
    equipment = Equipment.query.get_or_404(equipment_id)
    
    # VERIFICA SE O EQUIPAMENTO TEM UM MODELO VINCULADO
    if not equipment.template:
        flash('Este equipamento não possui um modelo de checklist vinculado.', 'danger')
        return redirect(url_for('main.index'))

    # BUSCA AS PERGUNTAS DO BANCO DE DADOS
    perguntas = equipment.template.perguntas.order_by('id').all()
    
    if request.method == 'POST':
        data = request.form
        respostas_json = json.loads(data.get('respostas'))
        observacoes = data.get('observacoes')
        assinatura = data.get('assinatura_colaborador')

        # Determinar status
        status = 'Conforme'
        nao_conforme_encontrado = False
        for item in respostas_json:
            if item['resposta'] == 'Não':
                status = 'Não Conforme'
                nao_conforme_encontrado = True
                break
        
        checklist = Checklist(
            equipamento_id=equipment.id,
            colaborador_id=current_user.id,
            respostas=respostas_json,
            observacoes=observacoes,
            assinatura_colaborador=assinatura,
            status=status
        )
        db.session.add(checklist)
        db.session.commit()

        if nao_conforme_encontrado:
            send_non_compliance_alert(checklist)
            flash('Checklist enviado. Uma não conformidade foi detectada e um alerta foi enviado.', 'warning')
        else:
            flash('Checklist preenchido e enviado com sucesso!', 'success')
        
        return redirect(url_for('main.index'))

    return render_template('fill_checklist.html', title='Preencher Checklist', equipment=equipment, perguntas=perguntas)


@bp.route('/checklists/pending')
@login_required
@role_required('GESTOR', 'COORDENADOR')
def pending_checklists():
    # Gestor só vê checklists do seu setor
    if current_user.cargo == UserRoles.GESTOR:
         pending = Checklist.query.join(Equipment).filter(Equipment.setor_id == current_user.setor_id, Checklist.assinatura_gestor == None).order_by(Checklist.data.desc()).all()
    else: # Coordenador vê todos
         pending = Checklist.query.filter(Checklist.assinatura_gestor == None).order_by(Checklist.data.desc()).all()
   
    return render_template('pending_checklists.html', title='Checklists Pendentes', checklists=pending)

@bp.route('/checklist/view/<int:checklist_id>', methods=['GET', 'POST'])
@login_required
@role_required('GESTOR', 'COORDENADOR')
def view_checklist(checklist_id):
    checklist = Checklist.query.get_or_404(checklist_id)

    # Validar se o gestor tem permissão para assinar
    if current_user.cargo == UserRoles.GESTOR and checklist.equipamento.setor_id != current_user.setor_id:
        flash('Você não tem permissão para validar este checklist.', 'danger')
        return redirect(url_for('main.pending_checklists'))

    if request.method == 'POST':
        assinatura = request.form.get('assinatura_gestor')
        if assinatura:
            checklist.assinatura_gestor = assinatura
            checklist.gestor_id = current_user.id
            if checklist.status == 'Não Conforme':
                 checklist.status = 'Não Conforme (Validado)'
            else:
                 checklist.status = 'Conforme (Validado)'

            db.session.commit()
            flash('Checklist validado e assinado com sucesso!', 'success')
            return redirect(url_for('main.pending_checklists'))

    return render_template('view_checklist.html', title='Validar Checklist', checklist=checklist)

# Rota para listar e criar Modelos de Checklist
@bp.route('/templates', methods=['GET', 'POST'])
@login_required
@role_required('GESTOR', 'COORDENADOR')
def manage_templates():
    form = TemplateForm()
    if form.validate_on_submit():
        new_template = ChecklistTemplate(nome=form.nome.data, descricao=form.descricao.data)
        db.session.add(new_template)
        db.session.commit()
        flash('Modelo de checklist criado com sucesso!', 'success')
        return redirect(url_for('main.manage_templates'))
    templates = ChecklistTemplate.query.all()
    return render_template('templates.html', title='Modelos de Checklist', form=form, templates=templates)

# Rota para gerenciar as perguntas de um modelo específico
@bp.route('/templates/<int:template_id>/questions', methods=['GET', 'POST'])
@login_required
@role_required('GESTOR', 'COORDENADOR')
def manage_questions(template_id):
    template = ChecklistTemplate.query.get_or_404(template_id)
    form = QuestionForm()
    if form.validate_on_submit():
        new_question = Question(texto=form.texto.data, template_id=template.id)
        db.session.add(new_question)
        db.session.commit()
        flash('Pergunta adicionada com sucesso!', 'success')
        return redirect(url_for('main.manage_questions', template_id=template.id))
    
    # Rota para apagar uma pergunta
    question_to_delete = request.args.get('delete')
    if question_to_delete:
        question = Question.query.get_or_404(question_to_delete)
        db.session.delete(question)
        db.session.commit()
        flash('Pergunta removida!', 'warning')
        return redirect(url_for('main.manage_questions', template_id=template.id))

    questions = template.perguntas.all()
    return render_template('manage_questions.html', title='Gerenciar Perguntas', form=form, template=template, questions=questions)

@bp.route('/checklist/<int:checklist_id>/download')
@login_required
def download_checklist_pdf(checklist_id):
    checklist = Checklist.query.get_or_404(checklist_id)
    
    # Renderiza o template do PDF em uma string HTML
    rendered_html = render_template('checklist_pdf.html', checklist=checklist)
    
    # Gera o PDF a partir do HTML usando WeasyPrint
    pdf = HTML(string=rendered_html).write_pdf()
    
    # Cria uma resposta Flask com o conteúdo do PDF
    return Response(pdf,
                    mimetype='application/pdf',
                    headers={'Content-Disposition': f'attachment;filename=checklist_{checklist.id}.pdf'})

# Adicione esta rota em app/routes.py
@bp.route('/history')
@login_required
@role_required('GESTOR', 'COORDENADOR')
def history():
    # No futuro, podemos adicionar filtros de data, setor, etc. aqui
    checklists = Checklist.query.order_by(Checklist.data.desc()).all()
    return render_template('history.html', title='Histórico de Checklists', checklists=checklists)