from sqlalchemy import Column, Integer, String, Boolean
from app.core.database import Base
from sqlalchemy.orm import relationship


# estrutura/modelo do DB do estabelecimento

class Estabelecimento(Base):
    __tablename__ = "estabelecimentos"

    # criacao da tabela dos estabelecimentos 
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    cnpj = Column(String(14), unique=True, index=True, nullable=False)
    chave_pix = Column(String(255), nullable=True)
    ativo = Column(Boolean, default=True)

    produtos = relationship("Produto", back_populates="estabelecimento")
    pedidos = relationship("Pedido", back_populates="estabelecimento")