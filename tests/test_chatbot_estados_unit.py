from decimal import Decimal

from app.adapters.message_provider import MensagemRecebida
from app.chatbot.estados_enum import EstadosChatbot
from app.chatbot.contexto import ContextoConversa
from app.chatbot.estados.bem_vindo import BemVindoEstado
from app.chatbot.estados.catalogo import CatalogoEstado
from app.chatbot.estados.carrinho import CarrinhoEstado
from app.chatbot.estados.pagamento import PagamentoEstado
from app.chatbot.estados.pedido_finalizado import PedidoFinalizadoEstado


def msg(texto):
    return MensagemRecebida(
        remetente="11999999999",
        texto=texto,
        tipo_mensagem="text",
        mensagem_id="fake-id",
    )


class TestBemVindoEstado:
    def test_apresenta_menu_na_primeira_interacao(self, db):
        estado = BemVindoEstado()
        resposta = estado.handle(ContextoConversa(), msg("qualquer coisa"), db)
        assert "catálogo" in resposta.texto.lower()
        assert resposta.novo_estado is None

    def test_escolher_catalogo_transiciona(self, db):
        estado = BemVindoEstado()
        resposta = estado.handle(ContextoConversa(), msg("1"), db)
        assert resposta.novo_estado == EstadosChatbot.CATALOGO.value

    def test_carrinho_vazio_nao_permite_finalizar(self, db):
        estado = BemVindoEstado()
        resposta = estado.handle(ContextoConversa(), msg("3"), db)
        assert "vazio" in resposta.texto.lower()
        assert resposta.novo_estado is None


class TestCatalogoEstado:
    def test_lista_produtos_do_estabelecimento(self, db, criar_estabelecimento,
                                               criar_produto):
        estab = criar_estabelecimento()
        criar_produto(estabelecimento_id=estab.id, nome="Picanha",
                      preco=Decimal("59.90"))
        contexto = ContextoConversa(estabelecimento_id=estab.id)
        estado = CatalogoEstado()
        resposta = estado.handle(contexto, msg(""), db)
        assert "Picanha" in resposta.texto
        assert len(contexto.produtos_disponiveis) == 1

    def test_catalogo_vazio_volta_ao_inicio(self, db, criar_estabelecimento):
        estab = criar_estabelecimento()
        contexto = ContextoConversa(estabelecimento_id=estab.id)
        estado = CatalogoEstado()
        resposta = estado.handle(contexto, msg(""), db)
        assert resposta.novo_estado == EstadosChatbot.BEM_VINDO.value

    def test_produto_fora_do_range_e_rejeitado(self, db, criar_estabelecimento,
                                               criar_produto):
        estab = criar_estabelecimento()
        criar_produto(estabelecimento_id=estab.id)
        contexto = ContextoConversa(estabelecimento_id=estab.id)
        estado = CatalogoEstado()
        estado.handle(contexto, msg(""), db)      # carrega catalogo
        resposta = estado.handle(contexto, msg("9"), db)  # produto inexistente
        assert "Opção inválida" in resposta.texto

    def test_quantidade_invalida_e_rejeitada(self, db, criar_estabelecimento,
                                             criar_produto):
        estab = criar_estabelecimento()
        criar_produto(estabelecimento_id=estab.id)
        contexto = ContextoConversa(estabelecimento_id=estab.id)
        estado = CatalogoEstado()
        estado.handle(contexto, msg(""), db)     # catalogo
        estado.handle(contexto, msg("1"), db)    # escolhe produto -> pede qtd
        resposta = estado.handle(contexto, msg("abc"), db)
        assert "Quantidade inválida" in resposta.texto

    def test_quantidade_de_zero_e_rejeitada(self, db, criar_estabelecimento,
                                            criar_produto):
        estab = criar_estabelecimento()
        criar_produto(estabelecimento_id=estab.id)
        contexto = ContextoConversa(estabelecimento_id=estab.id)
        estado = CatalogoEstado()
        estado.handle(contexto, msg(""), db)
        estado.handle(contexto, msg("1"), db)
        resposta = estado.handle(contexto, msg("0"), db)
        assert "maior que zero" in resposta.texto.lower()

    def test_fluxo_completo_de_adicao(self, db, criar_estabelecimento, criar_produto):
        estab = criar_estabelecimento()
        criar_produto(estabelecimento_id=estab.id, nome="Picanha",
                      preco=Decimal("59.90"))
        contexto = ContextoConversa(estabelecimento_id=estab.id)
        estado = CatalogoEstado()
        estado.handle(contexto, msg(""), db)
        estado.handle(contexto, msg("1"), db)
        resposta = estado.handle(contexto, msg("1.5"), db)

        assert len(contexto.carrinho) == 1
        assert contexto.carrinho[0]["nome"] == "Picanha"
        assert contexto.carrinho[0]["quantidade"] == 1.5
        assert resposta.novo_estado == EstadosChatbot.CARRINHO.value


class TestCarrinhoEstado:
    def test_finalizar_cria_pedido_e_vai_pagamento(self, db, criar_estabelecimento,
                                                   criar_cliente, criar_produto,
                                                   criar_pedido):
        estab = criar_estabelecimento()
        cliente = criar_cliente()
        contexto = ContextoConversa(
            estabelecimento_id=estab.id,
            cliente_id=cliente.id,
            carrinho=[{
                "produto_id": None,
                "nome": "Picanha",
                "quantidade": 1.5,
                "preco_unitario": 59.90,
                "unidade_medida": "KG",
            }],
        )
        estado = CarrinhoEstado()
        resposta = estado.handle(contexto, msg("3"), db)
        assert contexto.pedido_id is not None
        assert resposta.novo_estado == EstadosChatbot.PAGAMENTO.value

    def test_carrinho_vazio_nao_permite_finalizar(self, db):
        contexto = ContextoConversa()
        estado = CarrinhoEstado()
        resposta = estado.handle(contexto, msg("3"), db)
        assert "vazio" in resposta.texto.lower()
        assert resposta.novo_estado is None


class TestPagamentoEstado:
    def test_mostra_chave_pix_e_total(self, db, criar_estabelecimento,
                                      criar_cliente, criar_pedido):
        estab = criar_estabelecimento(chave_pix="pix@teste.com")
        cliente = criar_cliente()
        pedido = criar_pedido(estabelecimento_id=estab.id, cliente_id=cliente.id)
        contexto = ContextoConversa(
            estabelecimento_id=estab.id,
            pedido_id=pedido.id,
            carrinho=[{
                "produto_id": None,
                "nome": "Picanha",
                "quantidade": 1,
                "preco_unitario": 59.90,
                "unidade_medida": "KG",
            }],
        )
        estado = PagamentoEstado()
        resposta = estado.handle(contexto, msg(""), db)
        assert "pix@teste.com" in resposta.texto
        assert "59.90" in resposta.texto

    def test_confirmar_pagamento_finaliza_pedido(self, db, criar_estabelecimento,
                                                 criar_cliente, criar_produto,
                                                 criar_pedido):
        estab = criar_estabelecimento()
        cliente = criar_cliente()
        criar_produto(estabelecimento_id=estab.id, nome="Picanha",
                      preco=Decimal("59.90"))
        pedido = criar_pedido(estabelecimento_id=estab.id, cliente_id=cliente.id)
        contexto = ContextoConversa(
            estabelecimento_id=estab.id,
            pedido_id=pedido.id,
            carrinho=[{
                "produto_id": None,
                "nome": "Picanha",
                "quantidade": 1,
                "preco_unitario": 59.90,
                "unidade_medida": "KG",
            }],
        )
        estado = PagamentoEstado()
        resposta = estado.handle(contexto, msg("1"), db)
        assert resposta.novo_estado == EstadosChatbot.PEDIDO_FINALIZADO.value
        assert pedido.status == "FINALIZADO"

    def test_cancelar_pedido_volta_ao_inicio(self, db, criar_estabelecimento,
                                             criar_cliente, criar_produto,
                                             criar_pedido):
        estab = criar_estabelecimento()
        cliente = criar_cliente()
        criar_produto(estabelecimento_id=estab.id, nome="Picanha",
                      preco=Decimal("59.90"))
        pedido = criar_pedido(estabelecimento_id=estab.id, cliente_id=cliente.id)
        contexto = ContextoConversa(estabelecimento_id=estab.id, pedido_id=pedido.id)
        estado = PagamentoEstado()
        resposta = estado.handle(contexto, msg("2"), db)
        assert resposta.novo_estado == EstadosChatbot.BEM_VINDO.value
        assert pedido.status == "ABERTO"


class TestPedidoFinalizadoEstado:
    def test_pergunta_novo_pedido_e_volta_ao_inicio(self, db):
        estado = PedidoFinalizadoEstado()
        resposta = estado.handle(ContextoConversa(), msg("1"), db)
        assert "novo pedido" in resposta.texto.lower()
        assert resposta.novo_estado == EstadosChatbot.BEM_VINDO.value