from flask import render_template, flash, redirect, url_for
from flask_login import current_user, login_user, logout_user

# Importa a instância 'app' e o 'db' do nosso pacote 'app'
from app import app, db
from app.models import Usuario

@app.route('/')
@app.route('/index')
def index():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    return f"Olá, {current_user.nome}! Bem-vindo ao sistema."

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    # Lógica de login virá aqui (com formulário)
    # Por enquanto, vamos criar um usuário de teste e logar com ele ao acessar a rota
    
    user = Usuario.query.filter_by(matricula='12345').first()
    if user is None:
        u = Usuario(matricula='12345', nome='Operador Teste', perfil='operador')
        u.set_password('123')
        db.session.add(u)
        db.session.commit()
        user = u
        
    login_user(user, remember=True)
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))