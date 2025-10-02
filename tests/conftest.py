import pytest
from app import create_app, db as _db
from config import TestingConfig
from app.models import User, Sector, UserRoles, ChecklistTemplate, Question, Equipment, Checklist, Alert
from sqlalchemy import text

@pytest.fixture(scope='session')
def app():
    """Cria a instância da aplicação para toda a sessão de testes."""
    app = create_app(config_class=TestingConfig)
    with app.app_context():
        yield app

@pytest.fixture(scope='session')
def db(app):
    """Cria as tabelas do banco uma vez por sessão e as remove no final."""
    _db.create_all()
    yield _db
    _db.drop_all()

@pytest.fixture(scope='function', autouse=True)
def session(db):
    """Garante que cada teste comece com um banco de dados limpo."""
    # Apaga todos os dados de todas as tabelas
    db.session.execute(text('DELETE FROM alert'))
    db.session.execute(text('DELETE FROM checklist'))
    db.session.execute(text('DELETE FROM equipment'))
    db.session.execute(text('DELETE FROM question'))
    db.session.execute(text('DELETE FROM checklist_template'))
    db.session.execute(text('DELETE FROM user'))
    db.session.execute(text('DELETE FROM sector'))
    db.session.commit()
    yield db.session

@pytest.fixture(scope='function')
def client(app):
    """Um cliente de teste para a aplicação."""
    return app.test_client()

# --- Fixtures de Dados ---

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