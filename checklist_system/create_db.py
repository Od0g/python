# create_db.py
from app import create_app, db

print("Iniciando a criação do banco de dados...")

# Cria uma instância da aplicação Flask
app = create_app()

# O 'app_context' garante que a aplicação esteja 'ativa' 
# para que o SQLAlchemy saiba a qual banco de dados se conectar.
with app.app_context():
    print("Contexto da aplicação carregado.")
    print(f"Conectando a: {app.config['SQLALCHEMY_DATABASE_URI']}")
    
    # Este comando inspeciona todos os seus modelos (User, Checklist, etc.)
    # e cria todas as tabelas correspondentes no banco de dados.
    db.create_all()
    
    print("Banco de dados e todas as tabelas foram criados com sucesso!")