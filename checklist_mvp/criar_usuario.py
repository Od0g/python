from app import create_app, db
from app.models import Usuario

app = create_app()
app.app_context().push()

if Usuario.query.filter_by(matricula='12345').first() is None:
    u = Usuario(matricula='12345', nome='Admin', perfil='gestor')
    u.set_password('12345')
    db.session.add(u)
    db.session.commit()
    print("Usuário criado!")
else:
    print("Usuário já existe!")
