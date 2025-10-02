from fastapi import Depends, HTTPException, status # Adicione status
from . import crud, models # Adicione models
from .models import UserRole # Adicione UserRole
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer

# --- Configuração de Hashing de Senha ---
# Usamos bcrypt, que é um algoritmo seguro e padrão da indústria.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- Configuração do JWT ---
# ESTAS CHAVES DEVEM SER SECRETAS E VIVER EM VARIÁVEIS DE AMBIENTE EM PRODUÇÃO!
SECRET_KEY = "SUA_CHAVE_SECRETA_SUPER_DIFICIL" # Troque por uma chave complexa
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 # O token expira em 60 minutos

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password, hashed_password):
    """Verifica se a senha fornecida corresponde ao hash armazenado."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    """Gera o hash de uma senha."""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Cria um novo token de acesso JWT."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# NOVA FUNÇÃO
def require_role(allowed_roles: list[UserRole]):
    """
    Fábrica de dependências que cria uma dependência para verificar o perfil do usuário.
    """
    def get_current_user_with_role(current_user: models.User = Depends(crud.get_current_active_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="O usuário não tem permissão para executar esta ação."
            )
        return current_user
    return get_current_user_with_role