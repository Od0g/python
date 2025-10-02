from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
#from ..main import templates # Importa a instância de templates do main
from fastapi.templating import Jinja2Templates

router = APIRouter(
    tags=["Pages"],
    include_in_schema=False # Oculta estas rotas da documentação da API (/docs)
)

# ADD
templates = Jinja2Templates(directory="app/templates")

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.get("/", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@router.get("/scan", response_class=HTMLResponse)
async def scan_page(request: Request):
    return templates.TemplateResponse("scan.html", {"request": request})

@router.get("/checklist/form/{identifier}", response_class=HTMLResponse)
async def checklist_form_page(request: Request, identifier: str):
    # Passamos o identifier para o template, que o JavaScript irá usar
    return templates.TemplateResponse("checklist_form.html", {"request": request, "identifier": identifier})

@router.get("/validate/{checklist_id}", response_class=HTMLResponse)
async def validate_checklist_page(request: Request, checklist_id: int):
    # Passamos o ID do checklist para o template. O JavaScript usará este ID.
    return templates.TemplateResponse("validate_form.html", {"request": request, "checklist_id": checklist_id})

@router.get("/reports", response_class=HTMLResponse)
async def reports_page(request: Request):
    return templates.TemplateResponse("reports.html", {"request": request})