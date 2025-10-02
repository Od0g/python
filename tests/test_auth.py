# tests/test_auth.py

def test_login_logout(client, new_user):
    """
    Testa o fluxo completo de login e logout de um usuário válido.
    """
    # 1. Tenta acessar uma página protegida (dashboard) sem estar logado
    response_get_dashboard_anon = client.get('/', follow_redirects=True)
    assert response_get_dashboard_anon.status_code == 200
    assert b'Login do Sistema' in response_get_dashboard_anon.data

    # 2. Faz o login com as credenciais corretas
    response_login = client.post('/auth/login', data={
        'email': 'test@example.com',
        'password': 'password123'
    }, follow_redirects=True)
    
    assert response_login.status_code == 200
    assert b'Dashboard' in response_login.data
    assert b'Ol\xc3\xa1, Test User' in response_login.data # 'Olá' em bytes

    # 3. Faz o logout
    response_logout = client.get('/auth/logout', follow_redirects=True)
    assert response_logout.status_code == 200
    assert b'Login do Sistema' in response_logout.data
    # CORREÇÃO AQUI
    assert b'Dashboard' not in response_logout.data


def test_login_invalid_password(client, new_user):
    """
    Testa a tentativa de login com uma senha incorreta.
    """
    response = client.post('/auth/login', data={
        'email': 'test@example.com',
        'password': 'wrongpassword'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Login sem sucesso' in response.data
    # CORREÇÃO AQUI
    assert b'Dashboard' not in response.data