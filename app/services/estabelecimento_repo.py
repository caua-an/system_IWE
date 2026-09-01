from sqlalchemy.orm import Session
from app.models.estabelecimento import Estabelecimento
from app.schemas.estabelecimento_schema import EstabelecimentoCreate

def criar_estabelecimento(db: Session, estabelecimento : EstabelecimentoCreate):
    db_estabelecimento = Estabelecimento(
        nome = estabelecimento.nome,
        cnpj = estabelecimento.cnpj,
        chave_pix = estabelecimento.pix
    )

    db.add(db_estabelecimento)
    db.commit()

    db.refresh(db_estabelecimento)

    return db_estabelecimento

def buscar_estabelecimento_cnpj(db: Session, cnpj:str):
    return db.query(Estabelecimento).filter(Estabelecimento.cnpj == cnpj).first()