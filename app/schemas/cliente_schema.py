from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# schema base para cliente
class ClienteBase(BaseModel):
    # inicialmente somente sera necessario o numero para criar um cliente

    telefone: str = Field(
        ...,
        # vai de 10 a 20 por causa das variadas formatacoes de um numero 
        min_length=10,
        max_length=20,
        description="numero para contato do cliente"
    )

class ClienteCreate(ClienteBase):
    pass

class ClienteUpdate(ClienteBase):

    nome: Optional[str] = Field(
        None,
        min_length=2, 
        max_length=100,
        description="nome do cliente"
    )

    endereco_entrega: Optional[str] = Field(
        None,
        max_length=255,
        description="endereco para entrega do pedido"
    )

class ClienteResponse(ClienteBase):

    id:int
    nome: Optional[str] = None
    endereco_entrega: Optional[str] = None
    data_cadastro : datetime

    class Config:
        from_attributes = True