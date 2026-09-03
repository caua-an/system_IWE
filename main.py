from fastapi import FastAPI
from app.core.database import engine, Base
from app.models import estabelecimento as modelo_estabelecimento
from app.api import estabelecimento as api_estabelecimento
from app.api import produto as api_produto



Base.metadata.create_all(bind=engine)

app = FastAPI(title="Chatbot API - CORE")

app.include_router(api_estabelecimento.router)
app.include_router(api_produto.router)
@app.get("/")
def health_check():
    return {"status": "API operando e o bd sincro"}