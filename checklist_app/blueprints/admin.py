# checklist_app/blueprints/admin.py

from flask import Blueprint, render_template, redirect, url_for, flash, request, Response
from flask_login import login_required, current_user
# Importe todas as classes de modelo necessárias aqui
from models import ChecklistRespostas, Colaborador, Setor, Usuario, ChecklistModelo
from app import db
import json
from datetime import datetime
import csv
from io import StringIO

admin = Blueprint('admin', __name__, template_folder='../templates/admin')

def has_permission(perfil_requerido):
    """Função auxiliar para verificar se o usuário logado tem o perfil necessário."""
    return current_user.is_authenticated and current_user.perfil == perfil_requerido

@admin.before_request
@login_required
def check_admin_permission():
    if not (current_user.perfil == 'administrador' or current_user.perfil == 'coordenador'):
        flash('Você não tem permissão para acessar esta página.', 'danger')
        return redirect(url_for('index'))

@admin.route('/admin_dashboard')
def admin_dashboard():
    return render_template('admin_dashboard.html')

@admin.route('/cadastrar_colaborador', methods=['GET', 'POST'])
def cadastrar_colaborador():
    if request.method == 'POST':
        # Lógica para processar o formulário de cadastro de colaborador
        nome = request.form.get('nome')
        setor_id = request.form.get('setor')
        lider_id = request.form.get('lider')
        avaliador_id = request.form.get('avaliador')

        novo_colaborador = Colaborador(
            nome=nome,
            setor_id=setor_id,
            lider_id=lider_id
        )
        
        avaliador = Usuario.query.get(avaliador_id)
        if avaliador:
            novo_colaborador.avaliadores.append(avaliador)

        db.session.add(novo_colaborador)
        db.session.commit()
        
        flash(f'Colaborador {nome} cadastrado com sucesso!', 'success')
        return redirect(url_for('admin.admin_dashboard'))

    setores = Setor.query.all()
    lideres = Usuario.query.filter_by(perfil='lider').all()
    avaliadores = Usuario.query.filter_by(perfil='avaliador').all()
    
    return render_template('cadastrar_colaborador.html', 
                           setores=setores, 
                           lideres=lideres, 
                           avaliadores=avaliadores)

@admin.route('/cadastrar_setor', methods=['GET', 'POST'])
def cadastrar_setor():
    if request.method == 'POST':
        nome_setor = request.form.get('nome_setor')
        
        setor_existente = Setor.query.filter_by(nome=nome_setor).first()
        if setor_existente:
            flash('Este setor já existe.', 'warning')
        else:
            novo_setor = Setor(nome=nome_setor)
            db.session.add(novo_setor)
            db.session.commit()
            flash(f'Setor "{nome_setor}" cadastrado com sucesso!', 'success')
        
        return redirect(url_for('admin.admin_dashboard'))

    return render_template('cadastrar_setor.html')


@admin.route('/cadastrar_modelo', methods=['GET', 'POST'])
def cadastrar_modelo():
    if request.method == 'POST':
        tipo_checklist = request.form.get('tipo_checklist')
        # Os itens virão de uma área de texto, separados por linha
        itens_string = request.form.get('itens').strip()
        itens_lista = [item.strip() for item in itens_string.split('\n') if item.strip()]

        if itens_lista:
            # Salvamos os itens como uma string JSON no banco de dados
            novo_modelo = ChecklistModelo(
                tipo=tipo_checklist,
                itens=json.dumps(itens_lista)
            )
            db.session.add(novo_modelo)
            db.session.commit()
            flash(f'Modelo de checklist "{tipo_checklist}" criado com sucesso!', 'success')
        else:
            flash('Não foi possível criar o modelo. Nenhum item foi fornecido.', 'danger')
        
        return redirect(url_for('admin.admin_dashboard'))

    return render_template('cadastrar_modelo.html')


@admin.route('/gerenciar_usuarios')
def gerenciar_usuarios():
    usuarios = Usuario.query.all()
    return render_template('gerenciar_usuarios.html', usuarios=usuarios)

@admin.route('/editar_usuario/<int:usuario_id>', methods=['GET', 'POST'])
def editar_usuario(usuario_id):
    usuario = Usuario.query.get_or_404(usuario_id)

    if request.method == 'POST':
        usuario.nome = request.form.get('nome')
        usuario.login = request.form.get('login')
        usuario.perfil = request.form.get('perfil')
        
        db.session.commit()
        flash('Informações do usuário atualizadas com sucesso!', 'success')
        return redirect(url_for('admin.gerenciar_usuarios'))

    return render_template('editar_usuario.html', usuario=usuario)

@admin.route('/excluir_usuario/<int:usuario_id>', methods=['POST'])
def excluir_usuario(usuario_id):
    usuario = Usuario.query.get_or_404(usuario_id)

    if usuario.id == current_user.id:
        flash('Você não pode excluir seu próprio usuário.', 'danger')
        return redirect(url_for('admin.gerenciar_usuarios'))
    
    db.session.delete(usuario)
    db.session.commit()
    flash('Usuário excluído com sucesso.', 'success')
    return redirect(url_for('admin.gerenciar_usuarios'))



@admin.route('/relatorios', methods=['GET'])
def gerar_relatorios():
    colaboradores = Colaborador.query.all()
    setores = Setor.query.all()
    
    # Filtros
    colaborador_id = request.args.get('colaborador_id', type=int)
    setor_id = request.args.get('setor_id', type=int)
    data_inicio_str = request.args.get('data_inicio')
    data_fim_str = request.args.get('data_fim')
    
    # Construir a query base
    query = ChecklistRespostas.query.join(Colaborador).join(Setor)

    # Aplicar filtros
    if colaborador_id:
        query = query.filter(ChecklistRespostas.colaborador_id == colaborador_id)
    if setor_id:
        query = query.filter(Colaborador.setor_id == setor_id)
    if data_inicio_str:
        data_inicio = datetime.strptime(data_inicio_str, '%Y-%m-%d')
        query = query.filter(ChecklistRespostas.data_preenchimento >= data_inicio)
    if data_fim_str:
        data_fim = datetime.strptime(data_fim_str, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
        query = query.filter(ChecklistRespostas.data_preenchimento <= data_fim)

    # Obter os resultados
    resultados = query.all()

    return render_template('relatorios.html', 
                           resultados=resultados, 
                           colaboradores=colaboradores, 
                           setores=setores)

@admin.route('/exportar_relatorio', methods=['GET'])
def exportar_relatorio():
    colaborador_id = request.args.get('colaborador_id', type=int)
    setor_id = request.args.get('setor_id', type=int)
    data_inicio_str = request.args.get('data_inicio')
    data_fim_str = request.args.get('data_fim')
    formato = request.args.get('formato', 'csv') # Opção para escolher o formato

    query = ChecklistRespostas.query.join(Colaborador).join(Setor)

    # ... (lógica de filtros, a mesma da rota anterior) ...

    resultados = query.all()
    
    # Gerar o arquivo CSV
    if formato == 'csv':
        output = StringIO()
        writer = csv.writer(output)
        
        # Cabeçalho do CSV
        writer.writerow(['Colaborador', 'Setor', 'Tipo', 'Data', 'Pontuação', 'Situação'])
        
        # Linhas de dados
        for res in resultados:
            writer.writerow([
                res.colaborador.nome,
                res.colaborador.setor.nome,
                res.modelo.tipo,
                res.data_preenchimento.strftime('%Y-%m-%d'),
                res.pontuacao_final,
                res.situacao
            ])
            
        csv_output = output.getvalue()
        
        # Criar a resposta de download
        response = Response(csv_output, mimetype='text/csv')
        response.headers['Content-Disposition'] = 'attachment; filename=relatorio_checklist.csv'
        return response

    flash('Formato de exportação não suportado.', 'danger')
    return redirect(url_for('admin.gerar_relatorios'))