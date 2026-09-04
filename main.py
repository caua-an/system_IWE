from fastapi import FastAPI
from app.core.database import engine, Base
from app.models import estabelecimento as modelo_estabelecimento
from app.models import pedido as modelo_pedido
from app.models import pedido_item as modelo_pedido_item
from app.models import conversa_sessao as modelo_conversa_sessao
from app.api import estabelecimento as api_estabelecimento
from app.api import produto as api_produto
from app.api import cliente as api_cliente
from app.api import pedido as api_pedido



Base.metadata.create_all(bind=engine)

app = FastAPI(title="Chatbot API - CORE")

app.include_router(api_estabelecimento.router)
app.include_router(api_produto.router)
app.include_router(api_cliente.router)
app.include_router(api_pedido.router)
@app.get("/")
def health_check():
    return {"status": "API operando e o bd sincro"}