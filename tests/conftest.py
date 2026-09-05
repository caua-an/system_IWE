from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.models.estabelecimento import Estabelecimento
from app.models.cliente import Cliente
from app.models.produto import Produto
from app.models.pedido import Pedido
from main import app

# ---------------------------------------------------------------------------
# STRATEGIA DE BANCO DE TESTE
#
# 1) SQLite EM MEMORIA: cada "conexao em memoria" cria um banco NOVO quando a
#    conexao fecha. Usamos StaticPool (1 unica conexao fixa) -> todos os testes
#    enxergam o MESMO banco/schema.
# 2) ISOLAMENTO POR RECRICAO: antes de cada teste fazemos create_all e depois
#    drop_all. Dados nunca vazam de um teste para o outro (simples e robusto).
#    Obs.: tentamos o padrao "transacao + rollback", mas no SQLite o commit
#    vazava dados entre testes; recriar o schema e 100% deterministico.
# 3) PRAGMA foreign_keys=ON: SQLite nao impoe FK por padrao (MySQL impoe).
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def engine():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(engine, "connect")
    def ligar_foreign_keys(dbapi_connection, _record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    return engine


@pytest.fixture
def db(engine):
    # recria o schema do zero -> isolamento total entre testes
    Base.metadata.create_all(engine)
    session = Session(engine)
    yield session
    session.close()
    Base.metadata.drop_all(engine)


@pytest.fixture
def client(db):
    # TestClient chama a app ASGI em processo (sem rede). O get_db real e
    # sobrescrito para devolver a sessao de teste.
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


# --- factories de seed (dados de apoio, um por dominio) --------------------

@pytest.fixture
def criar_estabelecimento(db):
    def _criar(nome="Acougue Teste", cnpj="12345678000199",
               chave_pix="contato@teste.com", ativo=True):
        estab = Estabelecimento(nome=nome, cnpj=cnpj, chave_pix=chave_pix, ativo=ativo)
        db.add(estab)
        db.commit()
        db.refresh(estab)
        return estab
    return _criar


@pytest.fixture
def criar_cliente(db):
    def _criar(telefone="11999999999", nome=None, endereco_entrega=None):
        cliente = Cliente(telefone=telefone, nome=nome, endereco_entrega=endereco_entrega)
        db.add(cliente)
        db.commit()
        db.refresh(cliente)
        return cliente
    return _criar


@pytest.fixture
def criar_produto(db):
    def _criar(estabelecimento_id, nome="Picanha", preco=Decimal("59.90"),
               unidade_medida="KG", ativo=True):
        produto = Produto(
            estabelecimento_id=estabelecimento_id,
            nome=nome,
            preco=preco,
            unidade_medida=unidade_medida,
            ativo=ativo,
        )
        db.add(produto)
        db.commit()
        db.refresh(produto)
        return produto
    return _criar


@pytest.fixture
def criar_pedido(db):
    def _criar(estabelecimento_id, cliente_id):
        pedido = Pedido(estabelecimento_id=estabelecimento_id, cliente_id=cliente_id)
        db.add(pedido)
        db.commit()
        db.refresh(pedido)
        return pedido
    return _criar