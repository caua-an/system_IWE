from sqlalchemy.orm import Session
from app.models.pedido_item import PedidoItem
from app.models.produto import Produto
from app.schemas.pedido_schema import PedidoItemCreate


def adicionar_item(
    db: Session,
    pedido_id: int,
    item: PedidoItemCreate,
) -> PedidoItem:
    # snapshot do produto: copia nome, preco e metrica antes de gravar
    if item.produto_id is not None:
        produto = (
            db.query(Produto)
            .filter(Produto.id == item.produto_id)
            .first()
        )
        if produto:
            item.preco_unitario = produto.preco
            item.unidade_medida = produto.unidade_medida
            item.nome = produto.nome

    db_item = PedidoItem(
        pedido_id=pedido_id,
        produto_id=item.produto_id,
        nome=item.nome,
        quantidade=item.quantidade,
        preco_unitario=item.preco_unitario,
        unidade_medida=item.unidade_medida,
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def listar_itens(db: Session, pedido_id: int) -> list[PedidoItem]:
    return db.query(PedidoItem).filter(PedidoItem.pedido_id == pedido_id).all()
