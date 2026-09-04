from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.pedido_schema import (
    PedidoCreate,
    PedidoResponse,
    PedidoUpdate,
    PedidoItemCreate,
    PedidoItemResponse,
)
from app.services import pedido_repo, pedido_item_repo, estabelecimento_repo, cliente_repo


router = APIRouter(
    prefix="/estabelecimentos/{estabelecimento_id}/pedidos",
    tags=["Pedidos"],
)


# criar pedido vazio para um estabelecimento
@router.post("/", response_model=PedidoResponse, status_code=status.HTTP_201_CREATED)
def criar_pedido(
    estabelecimento_id: int,
    payload: PedidoCreate,
    db: Session = Depends(get_db),
):
    # coerencia do path com o body
    if payload.estabelecimento_id != estabelecimento_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inconsistencia: ID do estabelecimento diferente do corpo de requisicao",
        )

    # estabelecimento precisa existir
    estab = estabelecimento_repo.buscar_estabelecimento_id(db, estabelecimento_id)
    if not estab:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Estabelecimento nao encontrado",
        )
    if not estab.ativo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Estabelecimento inativo nao pode receber pedidos",
        )

    # cliente precisa existir
    cliente = cliente_repo.buscar_cliente_por_id(db, payload.cliente_id)
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente nao encontrado",
        )

    return pedido_repo.criar_pedido(db=db, pedido=payload)


# adicionar item ao pedido (snapshot automatico do produto)
@router.post(
    "/{pedido_id}/itens",
    response_model=PedidoItemResponse,
    status_code=status.HTTP_201_CREATED,
)
def adicionar_item(
    estabelecimento_id: int,
    pedido_id: int,
    payload: PedidoItemCreate,
    db: Session = Depends(get_db),
):
    pedido = pedido_repo.buscar_pedido(db, pedido_id, estabelecimento_id)
    if not pedido:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pedido nao encontrado neste estabelecimento",
        )
    if pedido.status != "ABERTO":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nao e possivel adicionar itens a um pedido que nao esta aberto",
        )

    return pedido_item_repo.adicionar_item(db=db, pedido_id=pedido_id, item=payload)


# atualizar status do pedido (fechar ou cancelar)
@router.patch("/{pedido_id}", response_model=PedidoResponse)
def atualizar_pedido(
    estabelecimento_id: int,
    pedido_id: int,
    payload: PedidoUpdate,
    db: Session = Depends(get_db),
):
    pedido = pedido_repo.buscar_pedido(db, pedido_id, estabelecimento_id)
    if not pedido:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pedido nao encontrado neste estabelecimento",
        )
    if pedido.status != "ABERTO":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nao e possivel alterar status de um pedido que nao esta aberto",
        )

    return pedido_repo.atualizar_status(db=db, pedido=pedido, novo_status=payload.status)


# listar pedidos de um estabelecimento
@router.get("/", response_model=list[PedidoResponse])
def listar_pedidos(
    estabelecimento_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    return pedido_repo.listar_pedidos(
        db=db, estabelecimento_id=estabelecimento_id, skip=skip, limit=limit
    )
