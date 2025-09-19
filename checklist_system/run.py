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


if __name__ == '__main__':
    app.run()