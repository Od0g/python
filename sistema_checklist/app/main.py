# app/main.py

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from . import models
from .database import engine
from .routers import auth, sectors, equipments, checklists, pages, reports

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Sistema de Checklists Virtuais",
    description="API para gerenciamento de checklists de equipamentos.",
    version="1.0.0"
)

origins = [
    "http://localhost", "http://localhost:8000",
    "http://127.0.0.1", "http://127.0.0.1:8000",
    "*" # Permite todas as origens para ambientes como o Gitpod
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Inclui todos os routers. A ordem aqui não importa muito.
app.include_router(auth.router)
app.include_router(sectors.router)
app.include_router(equipments.router)
app.include_router(checklists.router)
app.include_router(reports.router)
app.include_router(pages.router) # O router que contém a rota "/"