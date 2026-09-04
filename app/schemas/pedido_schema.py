from pydantic import BaseModel, Field
from typing import Literal
from decimal import Decimal
from datetime import datetime


# schema base para um item do pedido
class PedidoItemBase(BaseModel):
    produto_id: int | None = Field(
        None,
        description="ID do produto no catalogo (nullable para sobreviver a inativacao do produto)"
    )
    nome: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Nome do item no momento do snapshot"
    )
    quantidade: Decimal = Field(
        ...,
        gt=0,
        decimal_places=3,
        description="Quantidade (suporta kg e unidade)"
    )
    preco_unitario: Decimal = Field(
        ...,
        gt=0,
        decimal_places=2,
        description="Preco congelado (snapshot) no momento do pedido"
    )
    unidade_medida: Literal["KG", "UNIDADE"] = Field(
        ...,
        description="Metrica de venda congelada no momento do pedido"
    )


# schema para criar um item dentro de um pedido existente
class PedidoItemCreate(PedidoItemBase):
    pass


# schema de resposta do item (herda campos base)
class PedidoItemResponse(PedidoItemBase):
    id: int
    pedido_id: int

    class Config:
        from_attributes = True


# schema base para pedido
class PedidoBase(BaseModel):
    estabelecimento_id: int = Field(
        ...,
        gt=0,
        description="Loja responsavel pelo pedido"
    )
    cliente_id: int = Field(
        ...,
        gt=0,
        description="Cliente que realizou o pedido"
    )


# schema para criar pedido
class PedidoCreate(PedidoBase):
    pass


# schema para atualizar status do pedido (fechar/cancelar)
class PedidoUpdate(BaseModel):
    status: Literal["FINALIZADO", "CANCELADO"] = Field(
        ...,
        description="Novo status do pedido"
    )


# schema de resposta com itens e valor calculado
class PedidoResponse(PedidoBase):
    id: int
    status: str
    criado_em: datetime
    atualizado_em: datetime

    class Config:
        from_attributes = True
