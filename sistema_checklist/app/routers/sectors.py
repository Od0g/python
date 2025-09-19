# app/routers/sectors.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from .. import crud, models, schemas
from ..database import get_db

router = APIRouter(
    prefix="/sectors",
    tags=["Sectors"],
    dependencies=[Depends(crud.get_current_active_user)] # Protege TODAS as rotas neste arquivo!
)

@router.post("/", response_model=schemas.Sector, status_code=status.HTTP_201_CREATED)
def create_new_sector(sector: schemas.SectorCreate, db: Session = Depends(get_db)):
    db_sector = crud.get_sector_by_name(db, name=sector.name)
    if db_sector:
        raise HTTPException(status_code=400, detail="Setor com este nome já existe.")
    return crud.create_sector(db=db, sector=sector)

@router.get("/", response_model=List[schemas.Sector])
def read_sectors(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    sectors = crud.get_sectors(db, skip=skip, limit=limit)
    return sectors