# app/notifications.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from .config import settings
from . import models

def send_validation_notification_email(manager: models.User, checklist: models.Checklist):
    subject = f"Novo Checklist para Validação: {checklist.equipment.name}"

    # URL para o frontend (exemplo)
    checklist_url = f"http://seusistema.com/validate/{checklist.id}"

    html_content = f"""
    <html>
    <body>
        <p>Olá, {manager.full_name},</p>
        <p>Um novo checklist foi preenchido por <strong>{checklist.collaborator.full_name}</strong> para o equipamento <strong>{checklist.equipment.name}</strong> e aguarda sua validação.</p>
        <p>Para revisar e validar, por favor, acesse o link abaixo:</p>
        <p><a href="{checklist_url}">Validar Checklist</a></p>
        <p>Atenciosamente,<br>Sistema de Checklists</p>
    </body>
    </html>
    """

    message = MIMEMultipart()
    message['From'] = settings.MAIL_FROM
    message['To'] = manager.email
    message['Subject'] = subject
    message.attach(MIMEText(html_content, 'html'))

    try:
        with smtplib.SMTP(settings.MAIL_SERVER, settings.MAIL_PORT) as server:
            if settings.MAIL_STARTTLS:
                server.starttls()
            server.login(settings.MAIL_USERNAME, settings.MAIL_PASSWORD)
            server.send_message(message)
            print(f"E-mail de notificação enviado para {manager.email}")
    except Exception as e:
        print(f"Falha ao enviar e-mail: {e}")