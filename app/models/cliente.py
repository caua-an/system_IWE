from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True)
    # por motivos de ser um chatbot telefonico, telefone tera fator identificavel maior que nome, por isso nome nullable=true
    telefone = Column(String(20), unique=True, index=True, nullable=False)
    nome = Column(String(100), nullable=True)
    endereco_entrega = Column(String(255), nullable=True)
    data_cadastro = Column(DateTime(timezone=True), server_default=func.now())

    pedidos = relationship("Pedido", back_populates="cliente")