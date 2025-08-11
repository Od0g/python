# checklist_app/blueprints/auth.py

from flask import Blueprint, render_template, request, url_for, flash, redirect
from models import Usuario
from app import db, bcrypt
from flask_login import login_user, logout_user, current_user, login_required

auth = Blueprint('auth', __name__, template_folder='../templates/auth')

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        # ... (lógica de registro, como antes)
        nome = request.form.get('nome')
        login = request.form.get('login')
        senha = request.form.get('senha')
        perfil = request.form.get('perfil')

        senha_hash = bcrypt.generate_password_hash(senha).decode('utf-8')

        novo_usuario = Usuario(
            nome=nome,
            login=login,
            senha=senha_hash,
            perfil=perfil
        )
        
        db.session.add(novo_usuario)
        db.session.commit()
        
        flash('Usuário criado com sucesso!', 'success')
        return redirect(url_for('auth.login'))
        
    return render_template('register.html')

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        login_form = request.form.get('login')
        senha_form = request.form.get('senha')
        
        usuario = Usuario.query.filter_by(login=login_form).first()
        
        if usuario and bcrypt.check_password_hash(usuario.senha, senha_form):
            login_user(usuario) # Loga o usuário
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Login ou senha incorretos.', 'danger')
            
    return render_template('login.html')

@auth.route('/logout')
def logout():
    logout_user() # Desloga o usuário
    flash('Você foi desconectado.', 'info')
    return redirect(url_for('auth.login'))