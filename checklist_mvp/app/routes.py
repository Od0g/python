# app/routes.py
from datetime import datetime
import pandas as pd
from flask import Response, render_template_string
from weasyprint import HTML
import os
from werkzeug.utils import secure_filename
from app.models import ItemTemplate, Checklist, ChecklistResposta
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from app import app, db
from app.models import Usuario, Ativo
from app.forms import LoginForm, AtivoForm

@app.route('/')
@app.route('/index')
@login_required # Protege a página, exigindo login
def index():
    # A página inicial agora será o dashboard de ativos
    return redirect(url_for('ativos'))

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
        flash('Login realizado com sucesso!', 'success')
        return redirect(url_for('index'))
        
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/ativos', methods=['GET', 'POST'])
@login_required
def ativos():
    form = AtivoForm()
    if form.validate_on_submit():
        # Lógica para adicionar novo ativo
        novo_ativo = Ativo(
            codigo=form.codigo.data,
            descricao=form.descricao.data,
            setor=form.setor.data
        )
        db.session.add(novo_ativo)
        db.session.commit()
        flash('Ativo cadastrado com sucesso!', 'success')
        return redirect(url_for('ativos'))
        
    # Lógica para buscar e listar os ativos existentes
    page = request.args.get('page', 1, type=int)
    lista_ativos = Ativo.query.order_by(Ativo.codigo).paginate(page=page, per_page=10)
    
    return render_template('ativos.html', form=form, lista_ativos=lista_ativos.items)

# Criar um usuário de teste se não existir
with app.app_context():
    if Usuario.query.filter_by(matricula='12345').first() is None:
        u = Usuario(matricula='12345', nome='Operador Teste', perfil='operador')
        u.set_password('123')
        db.session.add(u)
        db.session.commit()

with app.app_context():
    if ItemTemplate.query.count() == 0:
        itens_padrao = ['Tela', 'Touch Screen', 'Carregador', 'Bateria', 'Leitor de Código de Barras']
        for item_desc in itens_padrao:
            db.session.add(ItemTemplate(descricao=item_desc))
        db.session.commit()

# Configuração para Uploads
UPLOAD_FOLDER = 'app/static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
@app.route('/index')
@login_required
def index():
    # Página inicial para o operador selecionar um ativo para checagem
    lista_ativos = Ativo.query.all()
    return render_template('dashboard.html', lista_ativos=lista_ativos)


@app.route('/checklist/<int:ativo_id>', methods=['GET', 'POST'])
@login_required
def checklist(ativo_id):
    ativo = Ativo.query.get_or_404(ativo_id)
    itens_template = ItemTemplate.query.all()

    if request.method == 'POST':
        # 1. Criar o cabeçalho do Checklist
        novo_checklist = Checklist(
            usuario_id=current_user.id,
            ativo_id=ativo.id,
            turno='Manhã' # Exemplo, pode ser melhorado
        )
        db.session.add(novo_checklist)
        db.session.commit()

        # 2. Iterar sobre os itens e salvar as respostas
        for item in itens_template:
            status = request.form.get(f'status_{item.id}')
            observacao = request.form.get(f'obs_{item.id}', '')
            foto = request.files.get(f'foto_{item.id}')

            foto_path = None
            if foto and allowed_file(foto.filename):
                filename = secure_filename(foto.filename)
                # Garante que o diretório de upload existe
                os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                foto_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                foto.save(foto_path)

            resposta = ChecklistResposta(
                checklist_id=novo_checklist.id,
                item_template_id=item.id,
                status=status,
                observacao=observacao,
                foto_path=foto_path
            )
            db.session.add(resposta)
        
        db.session.commit()
        flash(f'Checklist do ativo {ativo.codigo} salvo com sucesso!', 'success')
        return redirect(url_for('index'))

    return render_template('checklist.html', ativo=ativo, itens_template=itens_template)

def query_checklists_filtrados(args):
    """Função auxiliar para reutilizar a lógica de filtro."""
    query = Checklist.query
    
    if args.get('data_inicio'):
        data_inicio = datetime.strptime(args.get('data_inicio'), '%Y-%m-%d')
        query = query.filter(Checklist.timestamp >= data_inicio)
    
    if args.get('data_fim'):
        data_fim = datetime.strptime(args.get('data_fim'), '%Y-%m-%d').replace(hour=23, minute=59, second=59)
        query = query.filter(Checklist.timestamp <= data_fim)
        
    if args.get('ativo_id'):
        query = query.filter(Checklist.ativo_id == args.get('ativo_id'))
        
    return query.order_by(Checklist.timestamp.desc()).all()


@app.route('/historico')
@login_required
def historico():
    checklists = query_checklists_filtrados(request.args)
    ativos = Ativo.query.all()
    return render_template('historico.html', checklists=checklists, ativos=ativos)


@app.route('/checklist/ver/<int:checklist_id>')
@login_required
def ver_checklist(checklist_id):
    checklist = Checklist.query.get_or_404(checklist_id)
    return render_template('ver_checklist.html', checklist=checklist)


@app.route('/export/excel')
@login_required
def export_excel():
    checklists = query_checklists_filtrados(request.args)
    
    # Preparando os dados
    data = []
    for cl in checklists:
        for resp in cl.respostas:
            data.append({
                'Checklist ID': cl.id,
                'Data': cl.timestamp.strftime('%Y-%m-%d %H:%M'),
                'Ativo': cl.ativo.codigo,
                'Operador': cl.usuario.nome,
                'Item': resp.item_template.descricao,
                'Status': resp.status,
                'Observação': resp.observacao
            })
            
    df = pd.DataFrame(data)
    
    # Gerando o arquivo Excel em memória
    output = pd.ExcelWriter('php://output') # truque para não salvar em disco
    df.to_excel(output, index=False, sheet_name='Checklists')
    output.close()
    
    return Response(
        output.getvalue(),
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={'Content-Disposition': 'attachment;filename=historico_checklists.xlsx'}
    )


@app.route('/export/pdf')
@login_required
def export_pdf():
    checklists = query_checklists_filtrados(request.args)
    
    # Renderiza um template HTML simples para o PDF
    # (Poderíamos criar um arquivo .html separado para isso, mas para simplificar faremos aqui)
    html_string = render_template_string("""
        <h1>Relatório de Checklists</h1>
        <p>Relatório gerado em: {{ now }}</p>
        <table border="1" style="width:100%; border-collapse: collapse;">
            <thead>
                <tr>
                    <th>ID</th><th>Data</th><th>Ativo</th><th>Operador</th><th>Status</th>
                </tr>
            </thead>
            <tbody>
            {% for cl in checklists %}
                <tr>
                    <td>{{ cl.id }}</td>
                    <td>{{ cl.timestamp.strftime('%d/%m/%Y %H:%M') }}</td>
                    <td>{{ cl.ativo.codigo }}</td>
                    <td>{{ cl.usuario.nome }}</td>
                    <td>{{ 'Com Falhas' if cl.respostas.filter_by(status='Falha').first() else 'OK' }}</td>
                </tr>
            {% endfor %}
            </tbody>
        </table>
    """, checklists=checklists, now=datetime.now().strftime('%d/%m/%Y %H:%M'))
    
    # Converte o HTML para PDF
    pdf = HTML(string=html_string).write_pdf()
    
    return Response(
        pdf,
        mimetype='application/pdf',
        headers={'Content-Disposition': 'attachment;filename=historico_checklists.pdf'}
    )

  