# routes.py
from flask import render_template, request, redirect, url_for, flash, send_file
from app import app, db
from models import ChecklistTemplate, Checklist, ChecklistItem
import base64
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import pandas as pd
from datetime import datetime
from PIL import Image # Importar a biblioteca Pillow
import os # Importar para manipulação de arquivos
import tempfile # Importar para criar arquivos temporários

@app.route('/')
def index():
    checklists = Checklist.query.all()
    return render_template('index.html', checklists=checklists)

@app.route('/criar_checklist', methods=['GET', 'POST'])
def criar_checklist():
    if request.method == 'POST':
        avaliador = request.form['avaliador']
        setor = request.form['setor']
        turno = request.form['turno']
        treinador = request.form['treinador']
        carga_horaria = request.form.get('carga_horaria')
        processo_treinamento = request.form.get('processo_treinamento')

        template = ChecklistTemplate.query.first()
        if not template:
            template = ChecklistTemplate(nome_checklist="Checklist de Treinamento Padrão", itens_json=["Item 1", "Item 2", "Item 3", "Item 4"])
            db.session.add(template)
            db.session.commit()

        novo_checklist = Checklist(
            template_id=template.id,
            avaliador=avaliador,
            setor=setor,
            turno=turno,
            treinador=treinador,
            carga_horaria=carga_horaria,
            processo_treinamento=processo_treinamento
        )
        db.session.add(novo_checklist)
        db.session.commit()

        for item_nome in template.itens_json:
            item = ChecklistItem(checklist_id=novo_checklist.id, item_nome=item_nome)
            db.session.add(item)
        db.session.commit()

        flash('Checklist de Treinamento criado com sucesso!', 'success')
        return redirect(url_for('preencher_checklist', checklist_id=novo_checklist.id))
    return render_template('criar_checklist.html')

@app.route('/preencher_checklist/<int:checklist_id>', methods=['GET', 'POST'])
def preencher_checklist(checklist_id):
    checklist = Checklist.query.get_or_404(checklist_id)
    if request.method == 'POST':
        for item in checklist.itens:
            item.valor_preenchido = request.form.get(f'item_{item.id}_valor')
            item.observacoes = request.form.get(f'item_{item.id}_obs')
        db.session.commit()

        # Processar Assinatura do Funcionário
        assinatura_funcionario_data_url = request.form.get('assinatura_funcionario_data')
        if assinatura_funcionario_data_url:
            header, encoded = assinatura_funcionario_data_url.split(",", 1)
            checklist.assinatura_funcionario_data = base64.b64decode(encoded)
            checklist.nome_funcionario_assinatura = request.form.get('nome_funcionario_assinatura')
            checklist.data_hora_funcionario_assinatura = datetime.utcnow()

        # Processar Assinatura do Gestor
        assinatura_gestor_data_url = request.form.get('assinatura_gestor_data')
        if assinatura_gestor_data_url:
            header, encoded = assinatura_gestor_data_url.split(",", 1)
            checklist.assinatura_gestor_data = base64.b64decode(encoded)
            checklist.nome_gestor_assinatura = request.form.get('nome_gestor_assinatura')
            checklist.data_hora_gestor_assinatura = datetime.utcnow()

        checklist.status = 'Concluído'
        db.session.commit()
        flash('Checklist preenchido e assinado com sucesso!', 'success')
        return redirect(url_for('index'))
    return render_template('preencher_checklist.html', checklist=checklist)

@app.route('/historico')
def historico():
    checklists = Checklist.query.order_by(Checklist.data_preenchimento.desc()).all()
    return render_template('historico.html', checklists=checklists)

@app.route('/gerar_pdf/<int:checklist_id>')
def gerar_pdf(checklist_id):
    checklist = Checklist.query.get_or_404(checklist_id)
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    c.drawString(100, height - 50, f"Checklist ID: {checklist.id}")
    c.drawString(100, height - 70, f"Data: {checklist.data_preenchimento.strftime('%d/%m/%Y')}")
    c.drawString(100, height - 90, f"Treinador: {checklist.treinador}")
    c.drawString(100, height - 110, f"Carga Horária: {checklist.carga_horaria or 'N/A'}")
    c.drawString(100, height - 130, f"Processo: {checklist.processo_treinamento or 'N/A'}")
    c.drawString(100, height - 150, f"Avaliador: {checklist.avaliador}")
    c.drawString(100, height - 170, f"Setor: {checklist.setor}")
    c.drawString(100, height - 190, f"Turno: {checklist.turno}")

    y_pos = height - 230
    c.drawString(100, y_pos, "Itens do Checklist:")
    y_pos -= 20
    for item in checklist.itens:
        c.drawString(120, y_pos, f"Item: {item.item_nome}")
        c.drawString(140, y_pos - 15, f"Valor: {item.valor_preenchido or 'N/A'}")
        c.drawString(140, y_pos - 30, f"Obs: {item.observacoes or 'N/A'}")
        y_pos -= 50
        if y_pos < 100:
            c.showPage()
            y_pos = height - 50

    img_width = 200
    img_height = 80

    # --- Assinatura do Funcionário ---
    if checklist.assinatura_funcionario_data:
        if y_pos < 250:
            c.showPage()
            y_pos = height - 50
        
        c.drawString(100, y_pos - 50, "Assinatura do Funcionário:")
        try:
            # Carrega a imagem binária do DB com Pillow
            img_pil_funcionario = Image.open(BytesIO(checklist.assinatura_funcionario_data))
            
            # --- NOVO: Lógica para garantir fundo branco e remover transparência ---
            if img_pil_funcionario.mode in ('RGBA', 'LA') or (img_pil_funcionario.mode == 'P' and 'transparency' in img_pil_funcionario.info):
                # Cria uma nova imagem com fundo branco
                background = Image.new("RGB", img_pil_funcionario.size, (255, 255, 255))
                # Cola a imagem da assinatura sobre o fundo branco, usando a máscara de alfa
                background.paste(img_pil_funcionario, (0, 0), img_pil_funcionario)
                img_pil_funcionario = background
            elif img_pil_funcionario.mode != 'RGB': # Converte para RGB se não for RGBA/LA ou Paleta transparente
                img_pil_funcionario = img_pil_funcionario.convert('RGB')
            # --- FIM NOVO ---
            
            # Cria um arquivo temporário para a imagem PNG
            with tempfile.NamedTemporaryFile(delete=True, suffix='.png') as temp_file_f:
                # Salva a imagem Pillow processada no arquivo temporário
                img_pil_funcionario.save(temp_file_f, format='PNG')
                temp_file_f.flush()
                
                # Passa o CAMINHO DO ARQUIVO TEMPORÁRIO para ReportLab
                c.drawImage(temp_file_f.name, 100, y_pos - 150, width=img_width, height=img_height)
                
            c.drawString(100, y_pos - 160, f"Assinado por: {checklist.nome_funcionario_assinatura or 'N/A'}")
            c.drawString(100, y_pos - 175, f"Em: {checklist.data_hora_funcionario_assinatura.strftime('%d/%m/%Y %H:%M')}")
        except Exception as e:
            c.drawString(100, y_pos - 100, f"Erro ao carregar assinatura do funcionário: {e}")
        y_pos -= 200

    # --- Assinatura do Gestor ---
    if checklist.assinatura_gestor_data:
        if y_pos < 250:
            c.showPage()
            y_pos = height - 50
        
        c.drawString(100, y_pos - 50, "Assinatura do Gestor:")
        try:
            # Carrega a imagem binária do DB com Pillow
            img_pil_gestor = Image.open(BytesIO(checklist.assinatura_gestor_data))
            
            # --- NOVO: Lógica para garantir fundo branco e remover transparência ---
            if img_pil_gestor.mode in ('RGBA', 'LA') or (img_pil_gestor.mode == 'P' and 'transparency' in img_pil_gestor.info):
                background = Image.new("RGB", img_pil_gestor.size, (255, 255, 255))
                background.paste(img_pil_gestor, (0, 0), img_pil_gestor)
                img_pil_gestor = background
            elif img_pil_gestor.mode != 'RGB':
                img_pil_gestor = img_pil_gestor.convert('RGB')
            # --- FIM NOVO ---
            
            # Cria um arquivo temporário para a imagem PNG
            with tempfile.NamedTemporaryFile(delete=True, suffix='.png') as temp_file_g:
                # Salva a imagem Pillow processada no arquivo temporário
                img_pil_gestor.save(temp_file_g, format='PNG')
                temp_file_g.flush()

                # Passa o CAMINHO DO ARQUIVO TEMPORÁRIO para ReportLab
                c.drawImage(temp_file_g.name, 100, y_pos - 150, width=img_width, height=img_height)
                
            c.drawString(100, y_pos - 160, f"Assinado por: {checklist.nome_gestor_assinatura or 'N/A'}")
            c.drawString(100, y_pos - 175, f"Em: {checklist.data_hora_gestor_assinatura.strftime('%d/%m/%Y %H:%M')}")
        except Exception as e:
            c.drawString(100, y_pos - 100, f"Erro ao carregar assinatura do gestor: {e}")

    c.save()
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name=f"checklist_treinamento_{checklist_id}.pdf", mimetype='application/pdf')


@app.route('/gerar_excel/<int:checklist_id>')
def gerar_excel(checklist_id):
    checklist = Checklist.query.get_or_404(checklist_id)
    data = []
    # Adicionando novos campos ao DataFrame
    base_data = {
        "Checklist ID": checklist.id,
        "Data Preenchimento": checklist.data_preenchimento.strftime('%d/%m/%Y'),
        "Treinador": checklist.treinador,
        "Carga Horária": checklist.carga_horaria,
        "Processo de Treinamento": checklist.processo_treinamento,
        "Avaliador": checklist.avaliador,
        "Setor": checklist.setor,
        "Turno": checklist.turno,
        "Status": checklist.status,
        "Nome Funcionário Assinatura": checklist.nome_funcionario_assinatura,
        "Data/Hora Funcionário Assinatura": checklist.data_hora_funcionario_assinatura.strftime('%d/%m/%Y %H:%M') if checklist.data_hora_funcionario_assinatura else 'N/A',
        "Nome Gestor Assinatura": checklist.nome_gestor_assinatura,
        "Data/Hora Gestor Assinatura": checklist.data_hora_gestor_assinatura.strftime('%d/%m/%Y %H:%M') if checklist.data_hora_gestor_assinatura else 'N/A'
    }

    if checklist.itens:
        for item in checklist.itens:
            row = base_data.copy()
            row["Item"] = item.item_nome
            row["Valor Preenchido"] = item.valor_preenchido
            row["Observacoes"] = item.observacoes
            data.append(row)
    else: # Caso não haja itens, ainda assim queremos a linha com os dados principais
        data.append(base_data)

    df = pd.DataFrame(data)
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='openpyxl')
    df.to_excel(writer, index=False, sheet_name='Checklist Treinamento Data')
    writer.close()
    output.seek(0)
    return send_file(output, as_attachment=True, download_name=f"checklist_treinamento_{checklist_id}.xlsx", mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')