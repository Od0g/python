import os
from functools import wraps
from datetime import datetime
from werkzeug.utils import secure_filename

from flask import render_template, flash, redirect, url_for, request, Response, render_template_string
from flask_login import current_user, login_user, logout_user, login_required

from app import app, db
# Removido import de send_email para simplificar, pode ser adicionado depois
# from app.email import send_email 
from app.models import Usuario, Ativo, Checklist, ChecklistResposta, TipoAtivo, ModeloChecklist, ItemModelo
from app.forms import LoginForm, AtivoForm, CadastroUsuarioForm, ModeloChecklistForm, ItemModeloForm

# --- DECORATOR DE ADMIN ---
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.perfil != 'admin':
            flash('Acesso negado. Esta área é restrita a administradores.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# --- ROTAS DE AUTENTICAÇÃO ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = Usuario.query.filter_by(matricula=form.matricula.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Matrícula ou senha inválida.', 'danger')
            return redirect(url_for('login'))
        login_user(user, remember=True)
        return redirect(url_for('index'))
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

# --- ROTAS DO OPERADOR ---
@app.route('/')
@app.route('/index')
@login_required
def index():
    lista_ativos = Ativo.query.all()
    return render_template('dashboard.html', lista_ativos=lista_ativos)

@app.route('/selecionar-modelo/<int:ativo_id>')
@login_required
def selecionar_modelo(ativo_id):
    ativo = Ativo.query.get_or_404(ativo_id)
    if not ativo.tipo_ativo or not ativo.tipo_ativo.modelos_checklist:
        flash('Nenhum modelo de checklist associado a este tipo de ativo.', 'warning')
        return redirect(url_for('index'))
    return render_template('selecionar_modelo.html', ativo=ativo, modelos=ativo.tipo_ativo.modelos_checklist)

@app.route('/checklist/<int:ativo_id>/<int:modelo_id>', methods=['GET', 'POST'])
@login_required
def checklist(ativo_id, modelo_id):
    ativo = Ativo.query.get_or_404(ativo_id)
    modelo = ModeloChecklist.query.get_or_404(modelo_id)
    
    if request.method == 'POST':
        novo_checklist = Checklist(usuario_id=current_user.id, ativo_id=ativo.id, modelo_id=modelo.id)
        db.session.add(novo_checklist)
        db.session.commit()
        for item in modelo.itens:
            status = request.form.get(f'status_{item.id}')
            observacao = request.form.get(f'obs_{item.id}', '')
            resposta = ChecklistResposta(checklist_id=novo_checklist.id, item_modelo_id=item.id, status=status, observacao=observacao)
            db.session.add(resposta)
        db.session.commit()
        flash('Checklist salvo com sucesso!', 'success')
        return redirect(url_for('index'))
        
    return render_template('checklist.html', ativo=ativo, modelo=modelo)


# --- ROTAS DE ADMINISTRAÇÃO ---
@app.route('/admin/usuarios', methods=['GET', 'POST'])
@login_required
@admin_required
def gerenciar_usuarios():
    form = CadastroUsuarioForm()
    if form.validate_on_submit():
        if Usuario.query.filter_by(matricula=form.matricula.data).first():
            flash('Matrícula já cadastrada.', 'danger')
        else:
            novo_usuario = Usuario(matricula=form.matricula.data, nome=form.nome.data, perfil=form.perfil.data)
            novo_usuario.set_password(form.password.data)
            db.session.add(novo_usuario)
            db.session.commit()
            flash('Usuário cadastrado com sucesso!', 'success')
            return redirect(url_for('gerenciar_usuarios'))
    lista_usuarios = Usuario.query.all()
    return render_template('gerenciar_usuarios.html', form=form, lista_usuarios=lista_usuarios)

@app.route('/admin/ativos', methods=['GET', 'POST'])
@login_required
@admin_required
def ativos():
    form = AtivoForm()
    if form.validate_on_submit():
        novo_ativo = Ativo(codigo=form.codigo.data, descricao=form.descricao.data, setor=form.setor.data, tipo_ativo=form.tipo_ativo.data)
        db.session.add(novo_ativo)
        db.session.commit()
        flash('Ativo cadastrado com sucesso!', 'success')
        return redirect(url_for('ativos'))
    lista_ativos = Ativo.query.all()
    return render_template('ativos.html', form=form, lista_ativos=lista_ativos)

@app.route('/admin/modelos', methods=['GET', 'POST'])
@login_required
@admin_required
def gerenciar_modelos():
    form = ModeloChecklistForm()
    if form.validate_on_submit():
        novo_modelo = ModeloChecklist(nome=form.nome.data, descricao=form.descricao.data)
        db.session.add(novo_modelo)
        db.session.commit()
        flash('Novo modelo criado!', 'success')
        return redirect(url_for('gerenciar_modelos'))
    modelos = ModeloChecklist.query.all()
    return render_template('gerenciar_modelos.html', modelos=modelos, form=form)

@app.route('/admin/modelos/<int:modelo_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def editar_modelo(modelo_id):
    modelo = ModeloChecklist.query.get_or_404(modelo_id)
    item_form = ItemModeloForm()
    tipos_ativo = TipoAtivo.query.all()
    if item_form.validate_on_submit():
        novo_item = ItemModelo(pergunta=item_form.pergunta.data, modelo_id=modelo.id)
        db.session.add(novo_item)
        db.session.commit()
        flash('Pergunta adicionada!', 'success')
        return redirect(url_for('editar_modelo', modelo_id=modelo.id))
    return render_template('editar_modelo.html', modelo=modelo, item_form=item_form, tipos_ativo=tipos_ativo)

@app.route('/admin/modelos/<int:modelo_id>/associar_tipo', methods=['POST'])
@login_required
@admin_required
def associar_tipo_modelo(modelo_id):
    modelo = ModeloChecklist.query.get_or_404(modelo_id)
    tipo_id = request.form.get('tipo_id')
    tipo = TipoAtivo.query.get_or_404(tipo_id)
    modelo.tipos_ativo.append(tipo)
    db.session.commit()
    flash(f'Modelo "{modelo.nome}" associado ao tipo "{tipo.nome}".', 'success')
    return redirect(url_for('editar_modelo', modelo_id=modelo.id))

# --- ROTAS DE HISTÓRICO E RELATÓRIOS (Simplificado) ---
@app.route('/historico')
@login_required
def historico():
    checklists = Checklist.query.order_by(Checklist.timestamp.desc()).all()
    return render_template('historico.html', checklists=checklists, ativos=[]) # Passando lista vazia de ativos por enquanto

@app.route('/checklist/ver/<int:checklist_id>')
@login_required
def ver_checklist(checklist_id):
    checklist = Checklist.query.get_or_404(checklist_id)
    return render_template('ver_checklist.html', checklist=checklist)