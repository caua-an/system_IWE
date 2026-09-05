from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Literal
from decimal import Decimal

# schema base para produto
class ProdutoBase(BaseModel):
    nome: str = Field(
        ..., 
        min_length=2,
        max_length=100,
        description="nome do item"
    )

    descricao: Optional[str] = Field(
        None,
        max_length=255,
        description="detalhamento do item"
    )

    preco: Decimal = Field(
        ...,
        # garantir preço maior que 0
        gt=0,
        decimal_places=2,
        description="valor monetario do produto"
    )

    unidade_medida : Literal["KG", "UNIDADE"] = Field(
        ...,
        description="metrica da venda"
    )


class ProdutoCreate(ProdutoBase):
    estabelecimento_id : int = Field(
        ...,
        gt=0,
        description="chave estrangeira para vincular produto com o estabelecimento"
    )
# schema para atualizacao (put/patch da api)
class ProdutoUpdate(BaseModel):
    nome: Optional[str] = Field(None, min_length=2, max_length=100)
    descricao: Optional[str] = Field(None, max_length=255)
    preco: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    unidade_medida: Optional[Literal["KG", "UNIDADE"]] = None
    ativo: Optional[bool] = None

# schema de resposta da api 
class ProdutoResponse(ProdutoBase):
    id:int
    estabelecimento_id:int
    ativo:bool

    model_config = ConfigDict(from_attributes=True)
    
