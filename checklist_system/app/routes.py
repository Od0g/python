from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import User, Sector, Equipment, Checklist, UserRoles
from app.forms import UserForm, SectorForm, EquipmentForm
from app.email import send_non_compliance_alert
import qrcode
import os
import json
from functools import wraps

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
    if form.validate_on_submit():
        equip = Equipment(nome=form.nome.data, setor_id=form.setor.data)
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
    
    # Lista de perguntas (pode vir de um modelo no futuro)
    perguntas = [
        "O equipamento está limpo e em boas condições visuais?",
        "Os cabos e conexões elétricas estão intactos?",
        "Há sinais de vazamento de fluidos?",
        "Os dispositivos de segurança (botões de emergência, guardas) estão funcionando?",
        "O equipamento está operando sem ruídos ou vibrações anormais?"
    ]

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