# tests/test_routes.py
from app import db # <-- IMPORTAÇÃO ADICIONADA
from app.models import Sector, Equipment, Checklist, Question
import json

def test_manage_sectors_requires_login(client):
    """Testa se a página de setores redireciona se o usuário não estiver logado."""
    response = client.get('/sectors', follow_redirects=True)
    assert response.status_code == 200
    assert b'Login do Sistema' in response.data

def test_create_new_sector(client, admin_user):
    """
    Testa o fluxo de criação de um novo setor por um usuário admin.
    """
    # 1. Faz o login como o usuário admin
    client.post('/auth/login', data={
        'email': admin_user.email,
        'password': 'adminpass'
    }, follow_redirects=True)

    # 2. Acessa a página de setores para verificar o estado inicial
    response_get = client.get('/sectors')
    assert response_get.status_code == 200
    assert b'Setor de Engenharia' not in response_get.data

    # 3. Envia o formulário para criar um novo setor
    response_post = client.post('/sectors', data={
        'nome': 'Setor de Engenharia'
    }, follow_redirects=True)
    
    # 4. Verifica o resultado
    assert response_post.status_code == 200
    assert b'Setor cadastrado com sucesso!' in response_post.data
    assert b'Setor de Engenharia' in response_post.data

def test_create_new_equipment(client, admin_user, template_fixture):
    """
    Testa o fluxo de criação de um novo equipamento.
    Este teste depende de um admin logado e de um modelo de checklist existente.
    """
    client.post('/auth/login', data={
        'email': admin_user.email,
        'password': 'adminpass'
    })

    setor_de_teste = Sector.query.filter_by(nome='Setor de Teste').first()
    
    form_data = {
        'nome': 'Furadeira de Impacto 500W',
        'setor': setor_de_teste.id,
        'template': template_fixture.id
    }

    response = client.post('/equipment', data=form_data, follow_redirects=True)

    assert response.status_code == 200
    assert b'Equipamento cadastrado e QR Code gerado!' in response.data
    assert b'Furadeira de Impacto 500W' in response.data
    
    equip = Equipment.query.filter_by(nome='Furadeira de Impacto 500W').first()
    assert equip is not None
    assert equip.setor.id == setor_de_teste.id

def test_collaborator_fills_checklist(client, new_user, template_fixture):
    """
    Testa o fluxo completo de um colaborador preenchendo um checklist.
    """
    setor_de_teste = Sector.query.filter_by(nome='Setor de Teste').first()
    equip = Equipment(
        nome='Equipamento para Checklist', 
        setor_id=setor_de_teste.id, 
        template_id=template_fixture.id
    )
    db.session.add(equip)
    db.session.commit()

    client.post('/auth/login', data={
        'email': new_user.email,
        'password': 'password123'
    })

    response_get = client.get(f'/checklist/{equip.id}')
    assert response_get.status_code == 200
    assert b'Checklist de Equipamento' in response_get.data
    assert b'Pergunta de teste?' in response_get.data

    form_data = {
        'respostas': json.dumps([{'pergunta': '1. Pergunta de teste?', 'resposta': 'Sim'}]),
        'observacoes': 'Tudo operando normalmente.',
        'assinatura_colaborador': 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII='
    }

    response_post = client.post(f'/checklist/{equip.id}', data=form_data)

    assert response_post.status_code == 302
    
    assert Checklist.query.count() == 1
    
    saved_checklist = Checklist.query.first()
    assert saved_checklist is not None
    assert saved_checklist.equipamento_id == equip.id
    assert saved_checklist.colaborador_id == new_user.id
    assert saved_checklist.status == 'Conforme'
    assert saved_checklist.observacoes == 'Tudo operando normalmente.'