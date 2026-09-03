from sqlalchemy.orm import Session
from app.models.produto import Produto
from app.schemas.produto_schema import ProdutoCreate

def criar_Produto(db:Session, produto: ProdutoCreate):
    db_produto = Produto(
        estabelecimento_id = produto.estabelecimento_id,
        nome = produto.nome,
        descricao = produto.descricao,
        preco = produto.preco,
        unidade_medida = produto.unidade_medida
    )

    db.add(db_produto)
    db.commit()
    db.refresh(db_produto)
    return db_produto


# funcoes de consulta do produto no db
def listar_produtos_por_estabelecimento(db:Session, estabelecimento_id: int, skip: int =0, limit: int = 100):
    return db.query(Produto).filter(
        Produto.estabelecimento_id == estabelecimento_id
    ).offset(skip).limit(limit).all()

def buscar_produtos_por_id(db: Session, produto_id: int, estabelecimento_id: int):
    return db.query(Produto).filter(
        Produto.id == produto_id,
        Produto.estabelecimento_id == estabelecimento_id
    ).first()