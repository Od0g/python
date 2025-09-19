import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import current_app, render_template

def send_email(subject, sender, recipients, text_body, html_body):
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ", ".join(recipients)
    
    part1 = MIMEText(text_body, 'plain')
    part2 = MIMEText(html_body, 'html')
    
    msg.attach(part1)
    msg.attach(part2)

    try:
        with smtplib.SMTP(current_app.config['MAIL_SERVER'], current_app.config['MAIL_PORT']) as server:
            if current_app.config['MAIL_USE_TLS']:
                server.starttls()
            server.login(current_app.config['MAIL_USERNAME'], current_app.config['MAIL_PASSWORD'])
            server.sendmail(sender, recipients, msg.as_string())
            print("E-mail enviado com sucesso!")
    except Exception as e:
        print(f"Falha ao enviar e-mail: {e}")

def send_non_compliance_alert(checklist):
    gestor = checklist.equipamento.setor.users.filter_by(cargo='GESTOR').first()
    coordenadores = User.query.filter_by(cargo='COORDENADOR').all()
    
    if not gestor and not coordenadores:
        print("Nenhum gestor ou coordenador encontrado para enviar o alerta.")
        return

    recipients = []
    if gestor:
        recipients.append(gestor.email)
    recipients.extend([c.email for c in coordenadores])
    
    subject = f"Alerta de Não Conformidade: Equipamento {checklist.equipamento.nome}"
    sender = current_app.config['MAIL_USERNAME']
    
    html_body = f"""
    <h1>Alerta de Não Conformidade</h1>
    <p>Uma não conformidade foi registrada para o equipamento <strong>{checklist.equipamento.nome}</strong> no setor <strong>{checklist.equipamento.setor.nome}</strong>.</p>
    <p><strong>Colaborador:</strong> {checklist.colaborador.nome}</p>
    <p><strong>Data:</strong> {checklist.data.strftime('%d/%m/%Y %H:%M')}</p>
    <p><strong>Observações:</strong> {checklist.observacoes}</p>
    <p>Por favor, acesse o sistema para validar o checklist e tomar as ações necessárias.</p>
    """
    text_body = f"Alerta de Não Conformidade para o equipamento {checklist.equipamento.nome}. Acesse o sistema para mais detalhes."
    
    send_email(subject, sender, recipients, text_body, html_body)
    
    # Registra o alerta no banco
    from app.models import Alert
    from app import db
    for recipient in recipients:
        alert = Alert(checklist_id=checklist.id, enviado_para=recipient)
        db.session.add(alert)
    db.session.commit()