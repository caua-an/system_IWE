from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.estabelecimento_schema import EstabelecimentoCreate, EstabelecimentoResponse
from app.services import estabelecimento_repo

router = APIRouter(prefix="/estabelecimentos", tags=["Estabelecimentos"])

@router.post("/", response_model=EstabelecimentoResponse, status_code=status.HTTP_201_CREATED)
def cadastrar_estabelecimento(payload: EstabelecimentoCreate, db: Session = Depends(get_db)):
    # checagem de duplicidade pelo cnpj 
    estabelecimento_existente = estabelecimento_repo.buscar_estabelecimento_cnpj(db, cnpj=payload.cnpj)

    if estabelecimento_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Existe um estabelecimento cadastrado com o mesmo CNPJ"
        )

    # uso do design pattern repository 
    novo_estabelecimento = estabelecimento_repo.criar_estabelecimento(db=db, estabelecimento=payload)
    return novo_estabelecimento

@router.get("/", response_model=list[EstabelecimentoResponse])
def listar_estabelecimentos(skip: int=0, limit: int=100, db: Session = Depends(get_db)):
    return estabelecimento_repo.listar_estabelecimento(db=db, skip=skip, limit=limit)