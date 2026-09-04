from sqlalchemy import Column, Integer, String, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class PedidoItem(Base):
    __tablename__ = "pedido_itens"

    id = Column(Integer, primary_key=True, index=True)
    pedido_id = Column(Integer, ForeignKey("pedidos.id"), nullable=False)
    # produto_id e nullable para o item sobreviver a inativacao do produto
    produto_id = Column(Integer, ForeignKey("produtos.id"), nullable=True)
    nome = Column(String(100), nullable=False)
    quantidade = Column(Numeric(10, 3), nullable=False)
    # preco e metrica congelados (snapshot) no momento do pedido
    preco_unitario = Column(Numeric(10, 2), nullable=False)
    unidade_medida = Column(String(20), nullable=False, default="KG")

    pedido = relationship("Pedido", back_populates="itens")