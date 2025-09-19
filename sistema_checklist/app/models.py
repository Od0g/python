import enum
from sqlalchemy import (Boolean, Column, Integer, String, DateTime,
                        ForeignKey, Enum as SQLAlchemyEnum, Text)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

# Importa a Base do nosso arquivo database.py
from .database import Base

class UserRole(str, enum.Enum):
    colaborador = "colaborador"
    gestor = "gestor"
    administrador = "administrador"

# ... (outros enums como ChecklistStatus, QuestionResponse virão aqui depois)
# NOVOS ENUMS
class ChecklistStatus(str, enum.Enum):
    concluido = "CONCLUÍDO" # Preenchido pelo colaborador, aguardando gestor
    validado = "VALIDADO"   # Aprovado pelo gestor

class QuestionResponse(str, enum.Enum):
    sim = "Sim"
    nao = "Não"
    parcial = "Parcial"
    nsp = "Não se aplica"

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)
    role = Column(SQLAlchemyEnum(UserRole), nullable=False)
    sector_id = Column(Integer, ForeignKey('sectors.id'), nullable=True)
    is_active = Column(Boolean, default=True)

    # Relacionamento com Setor (será definido abaixo)
    sector = relationship("Sector", back_populates="users")

class Sector(Base):
    __tablename__ = 'sectors'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    
    # Um setor pode ter vários usuários (colaboradores/gestores)
    users = relationship("User", back_populates="sector")
    
    # Um setor pode ter um gestor principal (opcional)
    manager_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    manager = relationship("User", foreign_keys=[manager_id])

class Equipment(Base):
    __tablename__ = 'equipments'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    location = Column(String(150))

    # Este campo armazenará o UUID que irá no QR Code.
    # Usamos um default factory para gerar um novo UUID para cada equipamento.
    qr_code_identifier = Column(String(255), unique=True, index=True, default=lambda: str(uuid.uuid4()))

    sector_id = Column(Integer, ForeignKey('sectors.id'), nullable=False)

    # Define o relacionamento inverso, para podermos acessar equipment.sector
    sector = relationship("Sector")

# NOVA CLASSE CHECKLIST
class Checklist(Base):
    __tablename__ = 'checklists'
    
    id = Column(Integer, primary_key=True, index=True)
    equipment_id = Column(Integer, ForeignKey('equipments.id'), nullable=False)
    collaborator_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    manager_id = Column(Integer, ForeignKey('users.id'), nullable=True) # Preenchido na validação
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    validated_at = Column(DateTime(timezone=True), nullable=True)
    
    status = Column(SQLAlchemyEnum(ChecklistStatus), default=ChecklistStatus.concluido)
    
    # Assinaturas serão salvas como strings longas (Base64)
    collaborator_signature = Column(Text, nullable=False)
    manager_signature = Column(Text, nullable=True)
    
    # Relacionamentos
    equipment = relationship("Equipment")
    collaborator = relationship("User", foreign_keys=[collaborator_id])
    manager = relationship("User", foreign_keys=[manager_id])
    
    # Este relacionamento nos permitirá acessar checklist.responses
    responses = relationship("Response", back_populates="checklist", cascade="all, delete-orphan")

# NOVA CLASSE RESPONSE
class Response(Base):
    __tablename__ = 'responses'
    
    id = Column(Integer, primary_key=True, index=True)
    checklist_id = Column(Integer, ForeignKey('checklists.id'), nullable=False)
    question = Column(String(255), nullable=False)
    answer = Column(SQLAlchemyEnum(QuestionResponse), nullable=False)
    comment = Column(Text, nullable=True)
    
    # Relacionamento inverso para acessar response.checklist
    checklist = relationship("Checklist", back_populates="responses")
