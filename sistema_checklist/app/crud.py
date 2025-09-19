from sqlalchemy.orm import Session
from jose import JWTError, jwt # Adicione jwt aqui
from fastapi import Depends # Adicione Depends aqui
from . import models, schemas, security
from .database import get_db # Adicione get_db aqui
from .exceptions import credentials_exception

def get_user_by_username(db: Session, username: str):
    """Busca um usuário pelo seu nome de usuário."""
    return db.query(models.User).filter(models.User.username == username).first()

def create_user(db: Session, user: schemas.UserCreate):
    """Cria um novo usuário no banco de dados."""
    hashed_password = security.get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        hashed_password=hashed_password,
        role=user.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# NOVA FUNÇÃO DE DEPENDÊNCIA
def get_current_user(token: str = Depends(security.oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except JWTError:
        raise credentials_exception
    
    user = get_user_by_username(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

def get_current_active_user(current_user: models.User = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def get_sector_by_name(db: Session, name: str):
    return db.query(models.Sector).filter(models.Sector.name == name).first()

def get_sectors(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Sector).offset(skip).limit(limit).all()

def create_sector(db: Session, sector: schemas.SectorCreate):
    db_sector = models.Sector(name=sector.name)
    db.add(db_sector)
    db.commit()
    db.refresh(db_sector)
    return db_sector

def get_equipments(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Equipment).offset(skip).limit(limit).all()

def create_equipment(db: Session, equipment: schemas.EquipmentCreate):
    db_equipment = models.Equipment(
        name=equipment.name,
        location=equipment.location,
        sector_id=equipment.sector_id
    )
    db.add(db_equipment)
    db.commit()
    db.refresh(db_equipment)
    return db_equipment

def create_checklist(db: Session, checklist: schemas.ChecklistCreate, collaborator_id: int):
    """
    Cria um novo checklist e todas as suas respostas associadas.
    """
    # 1. Cria o objeto principal do Checklist
    db_checklist = models.Checklist(
        equipment_id=checklist.equipment_id,
        collaborator_id=collaborator_id,
        collaborator_signature=checklist.collaborator_signature
        # O status default já é 'concluido'
    )
    
    # 2. Adiciona o checklist à sessão para que ele tenha um ID
    db.add(db_checklist)
    db.flush() # 'flush' envia para o DB mas não commita a transação, útil para obter o ID
    
    # 3. Cria os objetos de Resposta associados
    for response_data in checklist.responses:
        db_response = models.Response(
            **response_data.dict(), # Desempacota o dicionário do Pydantic
            checklist_id=db_checklist.id
        )
        db.add(db_response)
        
    # 4. Commita a transação para salvar tudo de uma vez
    db.commit()
    
    # 5. Refresca o objeto para carregar os relacionamentos
    db.refresh(db_checklist)
    return db_checklist