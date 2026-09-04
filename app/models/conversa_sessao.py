from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from app.core.database import Base


class ConversaSessao(Base):
    __tablename__ = "conversa_sessoes"

    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    estabelecimento_id = Column(Integer, ForeignKey("estabelecimentos.id"), nullable=False)
    estado_atual = Column(String(30), nullable=False, default="BEM_VINDO")
    # contexto serializado (ex.: carrinho em construcao) em JSON
    contexto = Column(Text, nullable=True)
    atualizado_em = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
