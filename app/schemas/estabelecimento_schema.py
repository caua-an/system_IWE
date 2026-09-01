from pydantic import BaseModel, Field
from typing import Optional


# definicao da regra de negocio base de um estabelecimento 
class EstabelecimentoBase(BaseModel):
    nome: str = Field(
        ..., min_length=2, max_length=100, description="Nome/Fantasia do estabelecimento"
    )

    cnpj : str = Field(
        ..., min_length=14, max_length=14, description="Cadastro nacional de pessoa juridica"
    )

    pix : Optional[str] = Field(
        ..., None, max_length=255, description="Chave pix do estabelecimento"
    )

class EstabelecimentoCreate(EstabelecimentoBase):
    pass
# schema de atualizacao 
class EstabelecimentoUpdate(BaseModel):
    nome : Optional[str] = Field(..., None, min_length=2, max_digits=100)
    cnpj : Optional[str] = Field(..., None, min_length=14, max_digits=14)
    pix : Optional[str] = Field(..., None, max_digits=100)
    ativo : Optional[bool] = None
# schema de resposta para o cliente
class EstabelecimentoResponse(EstabelecimentoBase):
    id : int
    ativo : bool

    class Config:

        from_attributes = True