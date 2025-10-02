# tests/test_models.py
from app.models import User, UserRoles, Sector

def test_new_user(new_user):
    """Testa a criação de um novo usuário e a verificação de senha."""
    assert new_user.email == 'test@example.com'
    assert new_user.check_password('password123') is True
    assert new_user.check_password('wrongpassword') is False
    assert new_user.cargo == UserRoles.COLABORADOR

def test_user_repr(new_user):
    """Testa a representação em string do objeto User."""
    assert repr(new_user) == f"<User: test@example.com>"