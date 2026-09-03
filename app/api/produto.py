from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.produto_schema import ProdutoCreate, ProdutoResponse
from app.services import produto_repo

router = APIRouter(prefix="/estabelecimentos/{estabelecimento_id}/produtos", tags=["Produtos"])

@router.post("/", response_model=ProdutoResponse, status_code=status.HTTP_201_CREATED)
def cadastrar_produto(estabelecimento_id: int, payload: ProdutoCreate, db: Session = Depends(get_db)):
    # checagem de imcompatibilidade de IDs
    if payload.estabelecimento_id != estabelecimento_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inconsistencia: ID do estabelecimento diferente do corpo de requisicao"
        )

    return produto_repo.criar_Produto(db=db, produto=payload)

@router.get("/", response_model=list[ProdutoResponse])
def listar_produtos(estabelecimento_id: int, skip: int = 0, limit: int = 100, db : Session = Depends(get_db)):
    return produto_repo.listar_produtos_por_estabelecimento(
        db=db,
        estabelecimento_id=estabelecimento_id,
        skip=skip,
        limit= limit
    )
    