from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from .. import crud, models, schemas
from ..database import get_db

router = APIRouter(
    prefix="/checklists",
    tags=["Checklists"],
    dependencies=[Depends(crud.get_current_active_user)] # Protege todas as rotas
)

@router.post("/", response_model=schemas.Checklist, status_code=status.HTTP_201_CREATED)
def submit_new_checklist(
    checklist: schemas.ChecklistCreate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(crud.get_current_active_user)
):
    """
    Endpoint para um colaborador submeter um novo checklist preenchido.
    """
    # Aqui poderíamos adicionar lógicas de negócio, como verificar se o equipamento
    # realmente existe ou se o usuário tem permissão para preencher este checklist.
    
    return crud.create_checklist(
        db=db, checklist=checklist, collaborator_id=current_user.id
    )