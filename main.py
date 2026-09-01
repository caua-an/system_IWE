from fastapi import FastAPI
from app.core.database import engine, Base
from app.models.estabelecimento import Estabelecimento


Base.metadata.create_all(bind=engine)

app = FastAPI(title="Chatbot API - CORE")

@app.get("/")
def health_check():
    return {"status": "API operando o banco corretamente"}