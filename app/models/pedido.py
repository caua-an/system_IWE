from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Pedido(Base):
    __tablename__ = "pedidos"

    id = Column(Integer, primary_key=True, index=True)
    estabelecimento_id = Column(Integer, ForeignKey("estabelecimentos.id"), nullable=False)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    status = Column(String(20), nullable=False, default="ABERTO")
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    atualizado_em = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    estabelecimento = relationship("Estabelecimento", back_populates="pedidos")
    cliente = relationship("Cliente", back_populates="pedidos")

    itens = relationship(
        "PedidoItem",
        back_populates="pedido",
        cascade="all, delete-orphan",
    )

    @property
    def valor_total(self):
        # valor total nao e persistido: calculado a partir dos itens (snapshot de preco)
        return sum(item.quantidade * item.preco_unitario for item in self.itens)