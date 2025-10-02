from app import create_app, db
# NOVAS IMPORTAÇÕES NECESSÁRIAS PARA O COMANDO
from app.models import User, Sector, Checklist, Alert, UserRoles

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db, 
        'User': User, 
        'Sector': Sector, 
        'Equipment': Equipment, 
        'Checklist': Checklist, 
        'Alert': Alert
    }

# COMANDO ADICIONADO AQUI
@app.cli.command("create-admin")
def create_admin():
    """Cria um usuário coordenador inicial."""
    # Primeiro, verifica se existe algum setor. Se não, cria um.
    if not Sector.query.first():
        setor_admin = Sector(nome='Administrativo')
        db.session.add(setor_admin)
        db.session.commit()
        print("Setor 'Administrativo' criado.")
    
    setor = Sector.query.first()
    email = input("Digite o email do Coordenador: ")
    nome = input("Digite o nome do Coordenador: ")
    password = input("Digite a senha: ")

    # Verifica se o email já existe
    if User.query.filter_by(email=email).first():
        print(f"Erro: O e-mail '{email}' já está em uso.")
        return

    user = User(email=email, nome=nome, cargo=UserRoles.COORDENADOR, setor_id=setor.id)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    print(f"Usuário Coordenador '{nome}' criado com sucesso!")

@app.cli.command("seed")
def seed():
    """Cria usuários e dados iniciais no banco de dados."""
    admin_email = os.environ.get('ADMIN_EMAIL', 'admin@example.com')
    admin_password = os.environ.get('ADMIN_PASSWORD', 'password')
    admin_nome = os.environ.get('ADMIN_NAME', 'Admin User')

    # Verifica se o setor 'Administrativo' existe, se não, cria
    setor = Sector.query.filter_by(nome='Administrativo').first()
    if not setor:
        setor = Sector(nome='Administrativo')
        db.session.add(setor)
        db.session.commit()
        print("Setor 'Administrativo' criado.")

    # Verifica se o admin já existe
    if User.query.filter_by(email=admin_email).first():
        print(f"Usuário admin '{admin_email}' já existe.")
    else:
        admin = User(
            email=admin_email,
            nome=admin_nome,
            cargo=UserRoles.COORDENADOR,
            setor_id=setor.id
        )
        admin.set_password(admin_password)
        db.session.add(admin)
        db.session.commit()
        print(f"Usuário admin '{admin_email}' criado com sucesso.")


if __name__ == '__main__':
    app.run()