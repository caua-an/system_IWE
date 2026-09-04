from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.cliente_schema import ClienteCreate, ClienteUpdate, ClienteResponse
from app.services import cliente_repo

router = APIRouter(prefix="/clientes", tags=["Clientes"])

@router.post("/", response_model=ClienteResponse, status_code=status.HTTP_201_CREATED)
def cadastrar_cliente(payload: ClienteCreate, db: Session = Depends(get_db)):
    cliente_existente = cliente_repo.buscar_cliente_por_telefone(db, payload.telefone)
    if cliente_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O cliente ja existe um cliente cadastrado com esse telefone"
        )

    return cliente_repo.criar_Cliente(db=db,cliente=payload)


@router.get("/{telefone}", response_model=ClienteResponse)
def buscar_cliente(telefone:str , db: Session = Depends(get_db)):
    cliente = cliente_repo.buscar_cliente_por_telefone(db=db, telefone=telefone)

    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail = "Cliente nao consta na base de dados"
        )

    return cliente

# apos o cliente entrar em um contato primario com o chatbot, podera preencher realmente seus dados
@router.patch("/{cliente_id}", response_model=ClienteResponse)
def atualizar_dados_cliente(cliente_id: int, payload: ClienteUpdate, db: Session = Depends(get_db)):
    cliente_atualizado = cliente_repo.atualizar_cliente(db=db, cliente_id=cliente_id, dados=payload)

    if not cliente_atualizado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente nao encontrado para atualizacao"
        )
    return cliente_atualizado