from sqlalchemy.orm import Session
from app.models.pedido import Pedido
from app.schemas.pedido_schema import PedidoCreate


def criar_pedido(db: Session, pedido: PedidoCreate) -> Pedido:
    db_pedido = Pedido(
        estabelecimento_id=pedido.estabelecimento_id,
        cliente_id=pedido.cliente_id,
    )
    db.add(db_pedido)
    db.commit()
    db.refresh(db_pedido)
    return db_pedido


def buscar_pedido(db: Session, pedido_id: int, estabelecimento_id: int) -> Pedido | None:
    return (
        db.query(Pedido)
        .filter(
            Pedido.id == pedido_id,
            Pedido.estabelecimento_id == estabelecimento_id,
        )
        .first()
    )


def listar_pedidos(
    db: Session,
    estabelecimento_id: int,
    skip: int = 0,
    limit: int = 100,
) -> list[Pedido]:
    return (
        db.query(Pedido)
        .filter(Pedido.estabelecimento_id == estabelecimento_id)
        .order_by(Pedido.criado_em.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def atualizar_status(db: Session, pedido: Pedido, novo_status: str) -> Pedido:
    pedido.status = novo_status
    db.commit()
    db.refresh(pedido)
    return pedido
