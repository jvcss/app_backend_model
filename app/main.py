from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import auth, teams
from app.db.session import engine_internal_sync
from app.db.base import Base

app = FastAPI(title="API Applicativo")

Base.metadata.create_all(bind=engine_internal_sync)

origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,         # Permite apenas as origens definidas na lista
    allow_credentials=True,        # Permite o envio de cookies e credenciais
    allow_methods=["*"],           # Permite todos os métodos (GET, POST, etc.)
    allow_headers=["*"],           # Permite todos os cabeçalhos
)


app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(teams.router, prefix="/api/teams", tags=["teams"])

@app.get("/")
def root():
    return {"message": "Bem-vindo à API do Applicativo. Aqui terá o OpenAPI da aplicação"}
