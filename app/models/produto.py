from sqlalchemy import Column, Integer, String, Boolean, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

# definição da tabela de produto generico
class Produto(Base):

    __tablename__ = "produtos"

    id = Column(Integer, primary_key=True, index=True)
    # chave estrangeira que vai conectar produto ao estabelecimento
    estabelecimento_id = Column(Integer, ForeignKey("estabelecimentos.id"), nullable=False)
    nome = Column(String(100), nullable=False)
    descricao = Column(String(255), nullable=True)
    preco = Column(Numeric(10,2), nullable=False)
    unidade_medida = Column(String(20), nullable=False, default="KG")
    ativo = Column(Boolean, default=True)

    # relacionamento orm
    estabelecimento = relationship("Estabelecimento", back_populates="produtos")
