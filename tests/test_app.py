# tests/test_app.py
from app import create_app
from config import TestingConfig

def test_app_creation():
    """Testa se a fábrica de aplicação funciona com a config de teste."""
    app = create_app(config_class=TestingConfig)
    assert app is not None
    assert app.config['TESTING'] is True
    assert 'sqlite:///:memory:' in app.config['SQLALCHEMY_DATABASE_URI']

def test_index_redirects_anonymous(client):
    """Testa se a página inicial (/) redireciona para o login para usuários anônimos."""
    response = client.get('/')
    # 302 é o código HTTP para redirecionamento
    assert response.status_code == 302
    assert '/auth/login' in response.headers['Location']