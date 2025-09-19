from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

from .. import crud, schemas, security
from ..database import get_db
from .. import crud, schemas, security, models
from ..exceptions import credentials_exception #

router = APIRouter(
    tags=["Authentication"]
)

@router.post("/token", response_model=schemas.Token)
def login_for_access_token(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Endpoint de login. Recebe um formulário com 'username' e 'password'.
    Retorna um token JWT se as credenciais estiverem corretas.
    """
    user = crud.get_user_by_username(db, username=form_data.username)
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        # A exceção ainda é usada aqui, mas agora vem do local centralizado
        raise credentials_exception
    
    access_token_expires = timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

# Endpoint de criação de usuário (vamos colocar aqui por enquanto)
@router.post("/users/", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
def create_new_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Cria um novo usuário. Em um sistema real, este endpoint seria
    protegido e acessível apenas por administradores.
    """
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Nome de usuário já registrado")
    return crud.create_user(db=db, user=user)

# NOVO ENDPOINT PROTEGIDO
@router.get("/users/me/", response_model=schemas.User)
def read_users_me(current_user: models.User = Depends(crud.get_current_active_user)):
    """
    Retorna os dados do usuário atualmente logado.
    Requer autenticação.
    """
    return current_user