from decimal import Decimal

from app.schemas.pedido_schema import PedidoCreate, PedidoItemCreate
from app.services import pedido_repo, pedido_item_repo


class TestPedidoRepo:
    def test_criar_pedido_aberto(self, db, criar_estabelecimento, criar_cliente):
        estab = criar_estabelecimento()
        cliente = criar_cliente()
        pedido = pedido_repo.criar_pedido(
            db, PedidoCreate(estabelecimento_id=estab.id, cliente_id=cliente.id)
        )
        assert pedido.id is not None
        assert pedido.status == "ABERTO"

    def test_buscar_pedido_respeita_estabelecimento(self, db, criar_estabelecimento,
                                                    criar_cliente):
        estab_a = criar_estabelecimento(cnpj="11111111000199")
        estab_b = criar_estabelecimento(cnpj="22222222000199")
        cliente = criar_cliente()
        pedido = pedido_repo.criar_pedido(
            db, PedidoCreate(estabelecimento_id=estab_a.id, cliente_id=cliente.id)
        )
        assert pedido_repo.buscar_pedido(db, pedido.id, estab_a.id).id == pedido.id
        assert pedido_repo.buscar_pedido(db, pedido.id, estab_b.id) is None

    def test_listar_pedidos_do_estabelecimento(self, db, criar_estabelecimento,
                                               criar_cliente):
        estab_a = criar_estabelecimento(cnpj="11111111000199")
        estab_b = criar_estabelecimento(cnpj="22222222000199")
        cliente = criar_cliente()
        pedido_repo.criar_pedido(
            db, PedidoCreate(estabelecimento_id=estab_a.id, cliente_id=cliente.id)
        )
        pedido_repo.criar_pedido(
            db, PedidoCreate(estabelecimento_id=estab_b.id, cliente_id=cliente.id)
        )
        assert len(pedido_repo.listar_pedidos(db, estab_a.id)) == 1
        assert len(pedido_repo.listar_pedidos(db, estab_b.id)) == 1

    def test_atualizar_status(self, db, criar_estabelecimento, criar_cliente):
        estab = criar_estabelecimento()
        cliente = criar_cliente()
        pedido = pedido_repo.criar_pedido(
            db, PedidoCreate(estabelecimento_id=estab.id, cliente_id=cliente.id)
        )
        pedido_repo.atualizar_status(db, pedido, "FINALIZADO")
        assert pedido.status == "FINALIZADO"


class TestPedidoItemSnapshot:
    """A regra central: preco, metrica e nome sao CONGELADOS na hora do pedido."""

    def test_snapshot_vem_do_catalogo_ignorando_payload(self, db, criar_estabelecimento,
                                                        criar_cliente, criar_produto,
                                                        criar_pedido):
        estab = criar_estabelecimento()
        cliente = criar_cliente()
        produto = criar_produto(estabelecimento_id=estab.id, nome="Picanha",
                                preco=Decimal("59.90"))
        pedido = criar_pedido(estabelecimento_id=estab.id, cliente_id=cliente.id)

        # payload com valores ERRADOS de proposito: o repo deve priorizar o catalogo
        item = pedido_item_repo.adicionar_item(
            db,
            pedido_id=pedido.id,
            item=PedidoItemCreate(
                produto_id=produto.id,
                nome="HACK",
                quantidade=Decimal("1.5"),
                preco_unitario=Decimal("0.01"),
                unidade_medida="UNIDADE",
            ),
        )
        assert item.nome == "Picanha"
        assert item.preco_unitario == Decimal("59.90")
        assert item.unidade_medida == "KG"

    def test_item_sem_produto_preserva_dados_informados(self, db, criar_estabelecimento,
                                                        criar_cliente, criar_pedido):
        # produto_id nullable: item sobrevive quando o produto sai do catalogo.
        # Sem produto, os dados informados (o snapshot manual) prevalecem.
        estab = criar_estabelecimento()
        cliente = criar_cliente()
        pedido = criar_pedido(estabelecimento_id=estab.id, cliente_id=cliente.id)
        item = pedido_item_repo.adicionar_item(
            db,
            pedido_id=pedido.id,
            item=PedidoItemCreate(
                produto_id=None,
                nome="Produto fora de catalogo",
                quantidade=Decimal("2"),
                preco_unitario=Decimal("10.00"),
                unidade_medida="UNIDADE",
            ),
        )
        assert item.produto_id is None
        assert item.nome == "Produto fora de catalogo"
        assert item.preco_unitario == Decimal("10.00")


class TestPedidoValorTotal:
    def test_valor_total_eh_soma_dos_snapshots(self, db, criar_estabelecimento,
                                               criar_cliente, criar_produto,
                                               criar_pedido):
        estab = criar_estabelecimento()
        cliente = criar_cliente()
        picanha = criar_produto(estabelecimento_id=estab.id, nome="Picanha",
                                preco=Decimal("59.90"))
        coxinha = criar_produto(estabelecimento_id=estab.id, nome="Coxinha",
                                preco=Decimal("7.50"), unidade_medida="UNIDADE")
        pedido = criar_pedido(estabelecimento_id=estab.id, cliente_id=cliente.id)

        pedido_item_repo.adicionar_item(
            db, pedido_id=pedido.id,
            item=PedidoItemCreate(
                produto_id=picanha.id, nome="Picanha",
                quantidade=Decimal("1.5"), preco_unitario=Decimal("59.90"),
                unidade_medida="KG",
            ),
        )
        pedido_item_repo.adicionar_item(
            db, pedido_id=pedido.id,
            item=PedidoItemCreate(
                produto_id=coxinha.id, nome="Coxinha",
                quantidade=Decimal("2"), preco_unitario=Decimal("7.50"),
                unidade_medida="UNIDADE",
            ),
        )

        # 1.5 * 59.90 + 2 * 7.50 = 89.85 + 15.00 = 104.85
        assert pedido.valor_total == Decimal("104.85")


class TestPedidoAPI:
    URL = "/estabelecimentos/{estab_id}/pedidos/"

    def test_criar_pedido_com_sucesso(self, client, criar_estabelecimento,
                                      criar_cliente):
        estab = criar_estabelecimento()
        cliente = criar_cliente()
        resp = client.post(
            self.URL.format(estab_id=estab.id),
            json={"estabelecimento_id": estab.id, "cliente_id": cliente.id},
        )
        assert resp.status_code == 201
        assert resp.json()["status"] == "ABERTO"

    def test_estabelecimento_inexistente_retorna_404(self, client, criar_cliente):
        cliente = criar_cliente()
        resp = client.post(
            self.URL.format(estab_id=999),
            json={"estabelecimento_id": 999, "cliente_id": cliente.id},
        )
        assert resp.status_code == 404

    def test_estabelecimento_inativo_retorna_400(self, client, criar_estabelecimento,
                                                 criar_cliente):
        estab = criar_estabelecimento(ativo=False)
        cliente = criar_cliente()
        resp = client.post(
            self.URL.format(estab_id=estab.id),
            json={"estabelecimento_id": estab.id, "cliente_id": cliente.id},
        )
        assert resp.status_code == 400

    def test_cliente_inexistente_retorna_404(self, client, criar_estabelecimento):
        estab = criar_estabelecimento()
        resp = client.post(
            self.URL.format(estab_id=estab.id),
            json={"estabelecimento_id": estab.id, "cliente_id": 999},
        )
        assert resp.status_code == 404

    def test_adicionar_item_em_pedido_finalizado_retorna_400(self, client, db,
                                                             criar_estabelecimento,
                                                             criar_cliente,
                                                             criar_produto,
                                                             criar_pedido):
        estab = criar_estabelecimento()
        cliente = criar_cliente()
        produto = criar_produto(estabelecimento_id=estab.id)
        pedido = criar_pedido(estabelecimento_id=estab.id, cliente_id=cliente.id)
        pedido_repo.atualizar_status(db, pedido, "FINALIZADO")

        resp = client.post(
            f"{self.URL.format(estab_id=estab.id)}{pedido.id}/itens",
            json={
                "produto_id": produto.id,
                "nome": "Picanha",
                "quantidade": 1,
                "preco_unitario": 59.90,
                "unidade_medida": "KG",
            },
        )
        assert resp.status_code == 400

    def test_finalizar_pedido_aberto(self, client, criar_estabelecimento, criar_cliente):
        estab = criar_estabelecimento()
        cliente = criar_cliente()
        pedido = client.post(
            self.URL.format(estab_id=estab.id),
            json={"estabelecimento_id": estab.id, "cliente_id": cliente.id},
        ).json()
        resp = client.patch(
            f"{self.URL.format(estab_id=estab.id)}{pedido['id']}",
            json={"status": "FINALIZADO"},
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "FINALIZADO"

    def test_status_so_muda_quando_aberto(self, client, criar_estabelecimento,
                                          criar_cliente):
        estab = criar_estabelecimento()
        cliente = criar_cliente()
        pedido = client.post(
            self.URL.format(estab_id=estab.id),
            json={"estabelecimento_id": estab.id, "cliente_id": cliente.id},
        ).json()
        client.patch(
            f"{self.URL.format(estab_id=estab.id)}{pedido['id']}",
            json={"status": "FINALIZADO"},
        )
        # pedido ja finalizado: tentar cancelar apos fechado deve falhar
        resp = client.patch(
            f"{self.URL.format(estab_id=estab.id)}{pedido['id']}",
            json={"status": "CANCELADO"},
        )
        assert resp.status_code == 400

    def test_status_invalido_retorna_422(self, client, criar_estabelecimento,
                                         criar_cliente):
        estab = criar_estabelecimento()
        cliente = criar_cliente()
        pedido = client.post(
            self.URL.format(estab_id=estab.id),
            json={"estabelecimento_id": estab.id, "cliente_id": cliente.id},
        ).json()
        resp = client.patch(
            f"{self.URL.format(estab_id=estab.id)}{pedido['id']}",
            json={"status": "ENTREGUE"},
        )
        assert resp.status_code == 422

    def test_listar_pedidos_somente_do_estabelecimento(self, client,
                                                       criar_estabelecimento,
                                                       criar_cliente):
        estab = criar_estabelecimento()
        cliente = criar_cliente()
        client.post(
            self.URL.format(estab_id=estab.id),
            json={"estabelecimento_id": estab.id, "cliente_id": cliente.id},
        )
        resp = client.get(self.URL.format(estab_id=estab.id))
        assert resp.status_code == 200
        assert len(resp.json()) == 1