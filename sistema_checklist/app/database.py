from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# URL de conexão para o banco de dados SQLite. 
# O arquivo checklist_system.db será criado na raiz do projeto.
DATABASE_URL = "sqlite:///./checklist_system.db"

# O 'engine' é o ponto de entrada para o banco de dados.
# O argumento connect_args é necessário apenas para o SQLite para permitir o uso em múltiplas threads.
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

# Cada instância de SessionLocal será uma sessão de banco de dados.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Usaremos esta Base para criar cada um dos modelos do ORM (tabelas).
Base = declarative_base()

# Função para obter uma sessão do banco de dados (será usada com Dependency Injection)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()