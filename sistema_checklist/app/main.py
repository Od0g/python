from fastapi import FastAPI
from . import models
from .database import engine
from .routers import auth, sectors, equipments, checklists 


# Cria todas as tabelas no banco de dados (só na primeira vez que rodar)
# Em um ambiente de produção, usaríamos algo como Alembic para migrações.
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Sistema de Checklists Virtuais",
    description="API para gerenciamento de checklists de equipamentos.",
    version="1.0.0"
)

# Inclui as rotas de autenticação que criamos
app.include_router(auth.router)
app.include_router(sectors.router)
app.include_router(equipments.router)
app.include_router(checklists.router) #

@app.get("/")
def read_root():
    return {"message": "Bem-vindo à API do Sistema de Checklists!"}