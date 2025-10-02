from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List
from ..security import require_role # Importe a nova função
from ..models import UserRole # Importe o enum UserRole
from fastapi import HTTPException # Adicione esta importação se não estiver lá
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

# NOVO ENDPOINT: Listar pendentes para o gestor logado
@router.get("/pending", response_model=List[schemas.Checklist])
def read_pending_checklists(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role([UserRole.gestor, UserRole.administrador]))
):
    """
    Lista todos os checklists que estão pendentes de validação
    para os setores do gestor logado.
    """
    return crud.get_pending_checklists_for_manager(db=db, manager_id=current_user.id)

# NOVO ENDPOINT: Validar um checklist
@router.put("/{checklist_id}/validate", response_model=schemas.Checklist)
def validate_checklist_by_manager(
    checklist_id: int,
    validation_data: schemas.ChecklistValidate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role([UserRole.gestor, UserRole.administrador]))
):
    """
    Valida um checklist, adicionando a assinatura do gestor e mudando o status.
    """
    db_checklist = crud.get_checklist_by_id(db=db, checklist_id=checklist_id)
    if not db_checklist:
        raise HTTPException(status_code=404, detail="Checklist não encontrado")

    # Lógica de segurança: O gestor pode validar este checklist?
    # (Verifica se o checklist pertence a um setor que ele gerencia)
    if db_checklist.equipment.sector.manager_id != current_user.id:
        raise HTTPException(status_code=403, detail="Não autorizado a validar este checklist.")

    if db_checklist.status != models.ChecklistStatus.concluido:
        raise HTTPException(status_code=400, detail="Este checklist não está pendente de validação.")

    return crud.validate_checklist(
        db=db,
        db_checklist=db_checklist,
        manager_id=current_user.id,
        signature=validation_data.manager_signature
    )

# NOVO ENDPOINT
@router.get("/{checklist_id}", response_model=schemas.Checklist)
def read_checklist_by_id(
    checklist_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(crud.get_current_active_user) # Garante que está logado
):
    """
    Busca os detalhes completos de um único checklist pelo seu ID.
    """
    db_checklist = crud.get_checklist_by_id(db, checklist_id=checklist_id)
    if not db_checklist:
        raise HTTPException(status_code=404, detail="Checklist não encontrado")

    # Opcional: Adicionar verificação de permissão (ex: o gestor só pode ver checklists do seu setor)
    # if current_user.role == UserRole.gestor and db_checklist.equipment.sector.manager_id != current_user.id:
    #     raise HTTPException(status_code=403, detail="Não autorizado a ver este checklist.")

    return db_checklist