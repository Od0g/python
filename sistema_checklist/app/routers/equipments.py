# app/routers/equipments.py
import io
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response
from sqlalchemy.orm import Session
from typing import List
import qrcode

from .. import crud, models, schemas
from ..database import get_db

router = APIRouter(
    prefix="/equipments",
    tags=["Equipments"],
    dependencies=[Depends(crud.get_current_active_user)]
)

@router.post("/", response_model=schemas.Equipment, status_code=status.HTTP_201_CREATED)
def create_new_equipment(equipment: schemas.EquipmentCreate, db: Session = Depends(get_db)):
    return crud.create_equipment(db=db, equipment=equipment)

@router.get("/", response_model=List[schemas.Equipment])
def read_equipments(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    equipments = crud.get_equipments(db, skip=skip, limit=limit)
    return equipments

@router.get("/{equipment_id}/qr-code")
def generate_equipment_qr_code(equipment_id: int, db: Session = Depends(get_db)):
    db_equipment = db.query(models.Equipment).filter(models.Equipment.id == equipment_id).first()
    if not db_equipment:
        raise HTTPException(status_code=404, detail="Equipamento não encontrado")

    # A URL que o QR Code irá conter. O frontend saberá como lidar com isso.
    # Em produção, use o domínio real.
    qr_data_url = f"https://seusistema.com/checklist/start/{db_equipment.qr_code_identifier}"

    # Gera a imagem do QR Code em memória
    img = qrcode.make(qr_data_url)
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    qr_bytes = buf.getvalue()

    return Response(content=qr_bytes, media_type="image/png")