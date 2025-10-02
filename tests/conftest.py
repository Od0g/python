import pytest
from app import create_app, db
from config import TestingConfig
from app.models import User, Sector, UserRoles, ChecklistTemplate # Adicione outros modelos se necessário

# --- APP E DB ---

@pytest.fixture(scope="session")
def app():
    """Cria a instância da aplicação para toda a sessão de testes."""
    app = create_app(config_class=TestingConfig)
    with app.app_context():
        yield app

@pytest.fixture(scope="session")
def db_setup(app):
    """Cria as tabelas no início da sessão e remove no final."""
    db.create_all()
    yield db
    db.drop_all()

# --- SESSION COM LIMPEZA EXPLÍCITA ---

@pytest.fixture(scope="function")
def session(db_setup):
    """
    Garante um banco de dados 100% limpo para cada teste.
    Deleta todos os dados de todas as tabelas antes de cada execução.
    """
    # Deleta os dados em ordem reversa de dependência para evitar erros de FK
    for table in reversed(db.metadata.sorted_tables):
        db.session.execute(table.delete())
    db.session.commit()
    return db.session

# --- CLIENTE DE TESTE ---

@pytest.fixture(scope="function")
def client(app, session):
    """Client de teste com a session limpa já configurada."""
    return app.test_client()


# --- FIXTURES DE DADOS (Sem alterações) ---

@pytest.fixture(scope="function")
def test_sector(session):
    sector = Sector(nome="Setor de Teste")
    session.add(sector)
    session.commit() # Usar commit aqui é mais seguro com essa estratégia
    return sector

@pytest.fixture(scope="function")
def new_user(session, test_sector):
    user = User(
        nome="Test User",
        email="test@example.com",
        cargo=UserRoles.COLABORADOR,
        setor_id=test_sector.id
    )
    user.set_password("password123")
    session.add(user)
    session.commit()
    return user

@pytest.fixture(scope="function")
def admin_user(session, test_sector):
    admin = User(
        nome="Admin User",
        email="admin@example.com",
        cargo=UserRoles.COORDENADOR,
        setor_id=test_sector.id
    )
    admin.set_password("adminpass")
    session.add(admin)
    session.commit()
    return admin