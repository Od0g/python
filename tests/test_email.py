# tests/test_email.py
from unittest.mock import patch
from app import db
from app.models import Sector, Equipment, Checklist, Alert
import json

# Usamos o decorador @patch para substituir o 'smtplib.SMTP' por um dublê
@patch('app.email.smtplib.SMTP')
def test_non_compliance_alert_is_sent(mock_smtp, client, admin_user, new_user, template_fixture):
    """
    Testa se um e-mail de alerta é enviado quando um checklist
    com não conformidade é submetido.
    """
    # 1. SETUP: Preparar o cenário
    # O 'admin_user' será o gestor que receberá o e-mail
    # O 'new_user' será o colaborador que preenche o checklist
    setor = Sector.query.filter_by(nome='Setor de Teste').first()
    
    # Atribui o setor correto ao colaborador
    new_user.setor_id = setor.id
    db.session.commit()
    
    equip = Equipment(
        nome='Equipamento Crítico', 
        setor_id=setor.id, 
        template_id=template_fixture.id
    )
    db.session.add(equip)
    db.session.commit()

    # Faz o login como o colaborador
    client.post('/auth/login', data={
        'email': new_user.email,
        'password': 'password123'
    })

    # 2. AÇÃO: Submeter um checklist com uma resposta "Não"
    form_data = {
        'respostas': json.dumps([{'pergunta': '1. Pergunta de teste?', 'resposta': 'Não'}]),
        'observacoes': 'Equipamento com defeito grave.',
        'assinatura_colaborador': 'data:image/png;base64,FAKE_SIGNATURE'
    }
    client.post(f'/checklist/{equip.id}', data=form_data)

    # 3. VERIFICAÇÃO (Assertions)
    # Verifica se o status do checklist foi salvo como "Não Conforme"
    saved_checklist = Checklist.query.first()
    assert saved_checklist.status == 'Não Conforme'

    # Verifica se a função de enviar e-mail foi chamada
    # mock_smtp.return_value é o objeto que simula o servidor
    # .__enter__() é por causa do 'with smtplib.SMTP(...) as server:'
    server_instance = mock_smtp.return_value.__enter__.return_value
    assert server_instance.sendmail.called
    
    # Verifica se o e-mail foi para o destinatário correto (o admin/coordenador)
    # sendmail é chamado com (remetente, [destinatarios], msg)
    args, _ = server_instance.sendmail.call_args
    remetente = args[0]
    destinatarios = args[1]
    assert admin_user.email in destinatarios

    # Verifica se um registro de Alerta foi criado no banco
    assert Alert.query.count() == 1
    alert_record = Alert.query.first()
    assert alert_record.checklist_id == saved_checklist.id
    assert alert_record.enviado_para == admin_user.email