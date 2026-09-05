import pytest
from pydantic import ValidationError

from app.schemas.produto_schema import ProdutoCreate
from app.services import produto_repo, estabelecimento_repo


class TestProdutoSchema:
    def test_preco_deve_ser_maior_que_zero(self):
        with pytest.raises(ValidationError):
            ProdutoCreate(
                estabelecimento_id=1,
                nome="Picanha",
                preco=0,
                unidade_medida="KG",
            )
        with pytest.raises(ValidationError):
            ProdutoCreate(
                estabelecimento_id=1,
                nome="Picanha",
                preco=-1,
                unidade_medida="KG",
            )

    def test_unidade_medida_restrita(self):
        with pytest.raises(ValidationError):
            ProdutoCreate(
                estabelecimento_id=1,
                nome="Picanha",
                preco=59.90,
                unidade_medida="LITRO",
            )

    def test_nome_minimo(self):
        with pytest.raises(ValidationError):
            ProdutoCreate(
                estabelecimento_id=1,
                nome="A",
                preco=59.90,
                unidade_medida="KG",
            )


class TestProdutoRepo:
    def test_criar_produto_no_estabelecimento(self, db, criar_estabelecimento,
                                              criar_produto):
        estab = criar_estabelecimento()
        produto = criar_produto(estabelecimento_id=estab.id)
        assert produto.id is not None
        assert produto.estabelecimento_id == estab.id

    def test_listar_produtos_isola_por_estabelecimento(self, db, criar_estabelecimento,
                                                       criar_produto):
        estab_a = criar_estabelecimento(cnpj="11111111000199")
        estab_b = criar_estabelecimento(cnpj="22222222000199")
        criar_produto(estabelecimento_id=estab_a.id, nome="Picanha")
        criar_produto(estabelecimento_id=estab_a.id, nome="Coxinha",
                      unidade_medida="UNIDADE")
        criar_produto(estabelecimento_id=estab_b.id, nome="Alcatra")

        produtos_a = produto_repo.listar_produtos_por_estabelecimento(db, estab_a.id)
        produtos_b = produto_repo.listar_produtos_por_estabelecimento(db, estab_b.id)

        assert {p.nome for p in produtos_a} == {"Picanha", "Coxinha"}
        assert {p.nome for p in produtos_b} == {"Alcatra"}


class TestProdutoAPI:
    URL = "/estabelecimentos/{estab_id}/produtos/"

    def test_cadastrar_produto_com_sucesso(self, client, criar_estabelecimento):
        estab = criar_estabelecimento()
        resp = client.post(
            self.URL.format(estab_id=estab.id),
            json={
                "estabelecimento_id": estab.id,
                "nome": "Picanha",
                "preco": 59.90,
                "unidade_medida": "KG",
            },
        )
        assert resp.status_code == 201
        assert resp.json()["nome"] == "Picanha"

    def test_estabelecimento_inexistente_retorna_404(self, client):
        resp = client.post(
            self.URL.format(estab_id=999),
            json={
                "estabelecimento_id": 999,
                "nome": "Picanha",
                "preco": 59.90,
                "unidade_medida": "KG",
            },
        )
        assert resp.status_code == 404

    def test_estabelecimento_inativo_retorna_400(self, client, criar_estabelecimento):
        estab = criar_estabelecimento(ativo=False)
        resp = client.post(
            self.URL.format(estab_id=estab.id),
            json={
                "estabelecimento_id": estab.id,
                "nome": "Picanha",
                "preco": 59.90,
                "unidade_medida": "KG",
            },
        )
        assert resp.status_code == 400

    def test_estabelecimento_id_inconsistente_retorna_400(self, client,
                                                          criar_estabelecimento):
        estab = criar_estabelecimento()
        resp = client.post(
            self.URL.format(estab_id=estab.id),
            json={
                "estabelecimento_id": estab.id + 100,
                "nome": "Picanha",
                "preco": 59.90,
                "unidade_medida": "KG",
            },
        )
        assert resp.status_code == 400

    def test_listar_produtos_do_estabelecimento(self, client, criar_estabelecimento,
                                                criar_produto):
        estab = criar_estabelecimento()
        criar_produto(estabelecimento_id=estab.id, nome="Picanha")
        criar_produto(estabelecimento_id=estab.id, nome="Coxinha",
                      unidade_medida="UNIDADE")
        resp = client.get(self.URL.format(estab_id=estab.id))
        assert resp.status_code == 200
        assert len(resp.json()) == 2