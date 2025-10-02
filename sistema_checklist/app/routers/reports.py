# app/routers/reports.py
import pandas as pd
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import io

from .. import crud, models, schemas
from ..database import get_db
from ..security import require_role
from ..models import UserRole

router = APIRouter(
    prefix="/reports",
    tags=["Reports"],
    dependencies=[Depends(require_role([UserRole.gestor, UserRole.administrador]))]
)

@router.get("/checklists", response_model=List[schemas.Checklist])
def get_checklists_report(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    sector_id: Optional[int] = None,
    equipment_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Endpoint para visualizar dados de relatório em JSON."""
    checklists = crud.get_filtered_checklists(db, start_date, end_date, sector_id, equipment_id)
    return checklists

@router.get("/checklists/export")
def export_checklists_report(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    sector_id: Optional[int] = None,
    equipment_id: Optional[int] = None,
    format: str = Query("csv", enum=["csv", "xlsx"]),
    db: Session = Depends(get_db)
):
    """Endpoint para exportar relatórios em CSV ou Excel."""
    checklists = crud.get_filtered_checklists(db, start_date, end_date, sector_id, equipment_id)

    # Estrutura os dados para o DataFrame
    data = []
    for c in checklists:
        for r in c.responses:
            data.append({
                "Checklist ID": c.id,
                "Data": c.created_at.strftime("%d/%m/%Y %H:%M"),
                "Equipamento": c.equipment.name,
                "Setor": c.equipment.sector.name,
                "Colaborador": c.collaborator.full_name,
                "Status": c.status.value,
                "Validado por": c.manager.full_name if c.manager else "",
                "Data Validação": c.validated_at.strftime("%d/%m/%Y %H:%M") if c.validated_at else "",
                "Pergunta": r.question,
                "Resposta": r.answer.value,
                "Comentário": r.comment,
            })

    if not data:
        return {"message": "Nenhum dado encontrado para exportar com os filtros selecionados."}

    df = pd.DataFrame(data)

    stream = io.BytesIO()
    filename = f"relatorio_checklists_{datetime.now().strftime('%Y%m%d')}"

    if format == "xlsx":
        df.to_excel(stream, index=False)
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        filename += ".xlsx"
    else: # CSV
        df.to_csv(stream, index=False)
        media_type = "text/csv"
        filename += ".csv"

    stream.seek(0)

    headers = {'Content-Disposition': f'attachment; filename="{filename}"'}
    return StreamingResponse(stream, media_type=media_type, headers=headers)