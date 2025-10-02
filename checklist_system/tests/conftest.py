# tests/conftest.py
import pytest
from app import create_app, db as _db
from app.models import User, Sector, UserRoles, ChecklistTemplate, Question, Equipment, Checklist, Alert
from config import TestingConfig

@pytest.fixture(scope='session')
def app():
    """Cria a aplicação uma vez por sessão de teste."""
    app = create_app(config_class=TestingConfig)
    with app.app_context():
        yield app

@pytest.fixture(scope='session')
def db(app):
    """Cria as tabelas do banco de dados uma vez por sessão."""
    _db.create_all()
    yield _db
    _db.drop_all()

@pytest.fixture(scope='function')
def session(db):
    """Garante que cada teste comece com um banco de dados limpo."""
    # Apaga todos os dados de todas as tabelas
    # A ordem é importante para respeitar as chaves estrangeiras
    Alert.query.delete()
    Checklist.query.delete()
    Equipment.query.delete()
    Question.query.delete()
    ChecklistTemplate.query.delete()
    User.query.delete()
    Sector.query.delete()
    db.session.commit()
    
    yield db.session

# O client não precisa mais da fixture 'session' diretamente
@pytest.fixture(scope='function')
def client(app):
    return app.test_client()

# --- Fixtures de Dados ---
# As fixtures agora recebem 'session' para usar o banco limpo
@pytest.fixture(scope='function')
def test_sector(session):
    sector = Sector(nome='Setor de Teste')
    session.add(sector)
    session.commit()
    return sector

@pytest.fixture(scope='function')
def new_user(session, test_sector):
    user = User(
        nome='Test User',
        email='test@example.com',
        cargo=UserRoles.COLABORADOR,
        setor_id=test_sector.id
    )
    user.set_password('password123')
    session.add(user)
    session.commit()
    return user

@pytest.fixture(scope='function')
def admin_user(session, test_sector):
    admin = User(
        nome='Admin User',
        email='admin@example.com',
        cargo=UserRoles.COORDENADOR,
        setor_id=test_sector.id
    )
    admin.set_password('adminpass')
    session.add(admin)
    session.commit()
    return admin

@pytest.fixture(scope='function')
def template_fixture(session):
    template = ChecklistTemplate(nome='Modelo de Teste Padrão')
    session.add(template)
    session.commit()
    question = Question(texto='Pergunta de teste?', template_id=template.id)
    session.add(question)
    session.commit()
    return template