from sqlalchemy.orm import Session
from app.models.estabelecimento import Estabelecimento
from app.schemas.estabelecimento_schema import EstabelecimentoCreate

def criar_estabelecimento(db: Session, estabelecimento : EstabelecimentoCreate):
    db_estabelecimento = Estabelecimento(
        nome = estabelecimento.nome,
        cnpj = estabelecimento.cnpj,
        chave_pix = estabelecimento.chave_pix
    )

    db.add(db_estabelecimento)
    db.commit()

    db.refresh(db_estabelecimento)

    return db_estabelecimento

def buscar_estabelecimento_cnpj(db: Session, cnpj:str):
    return db.query(Estabelecimento).filter(Estabelecimento.cnpj == cnpj).first()

def buscar_estabelecimento_id(db: Session, estabelecimento_id: int):
    return db.query(Estabelecimento).filter(Estabelecimento.id == estabelecimento_id).first()

def listar_estabelecimento(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Estabelecimento).offset(skip).limit(limit).all()