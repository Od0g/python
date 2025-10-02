from pydantic import BaseModel, EmailStr
from typing import Optional
from typing import List
from datetime import datetime
from .models import QuestionResponse, ChecklistStatus, UserRole 

# --- Esquemas para Usuários ---

# Propriedades base compartilhadas
class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: str

# Propriedades recebidas na criação de um usuário
class UserCreate(UserBase):
    password: str
    role: UserRole

# Propriedades contidas em um usuário retornado pela API
class User(UserBase):
    id: int
    is_active: bool
    role: UserRole
    sector_id: Optional[int] = None

    # Configuração para permitir que o Pydantic leia dados de modelos ORM
    class Config:
        from_attributes = True

# --- Esquemas para Autenticação ---
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# --- Esquemas para Setores ---
class SectorBase(BaseModel):
    name: str

class SectorCreate(SectorBase):
    pass

class Sector(SectorBase):
    id: int

    class Config:
        from_attributes = True

# --- Esquemas para Equipamentos ---
class EquipmentBase(BaseModel):
    name: str
    location: Optional[str] = None
    sector_id: int

class EquipmentCreate(EquipmentBase):
    pass

# Este schema será usado para retornar dados, incluindo o do setor relacionado.
class Equipment(EquipmentBase):
    id: int
    qr_code_identifier: str
    sector: Sector # Aninha o schema do Setor para um retorno mais completo

    class Config:
        from_attributes = True


class ResponseBase(BaseModel):
    question: str
    answer: QuestionResponse
    comment: Optional[str] = None

class ResponseCreate(ResponseBase):
    pass

class Response(ResponseBase):
    id: int
    checklist_id: int

    class Config:
        from_attributes = True

# --- Esquemas para Checklists ---
class ChecklistBase(BaseModel):
    equipment_id: int

class ChecklistCreate(ChecklistBase):
    collaborator_signature: str
    responses: List[ResponseCreate] # Uma lista de respostas

# Schema para retornar um checklist completo
class Checklist(ChecklistBase):
    id: int
    collaborator_id: int
    status: ChecklistStatus
    created_at: datetime # Certifique-se de ter 'from datetime import datetime' no topo do arquivo
    
    # Aninha os dados completos para um retorno rico
    collaborator: User
    equipment: Equipment
    responses: List[Response]

    class Config:
        from_attributes = True

class ChecklistValidate(BaseModel):
    manager_signature: str