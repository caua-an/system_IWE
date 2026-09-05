from decimal import Decimal

from app.adapters.message_provider import MensagemRecebida
from app.chatbot.maquina_estados import MaquinaEstados
from app.models.conversa_sessao import ConversaSessao
from app.models.pedido import Pedido
from app.services import estabelecimento_repo, cliente_repo


def msg(texto):
    return MensagemRecebida(
        remetente="11999999999",
        texto=texto,
        tipo_mensagem="text",
        mensagem_id="fake-id",
    )


class TestFluxoIntegrado:
    """Prova o caminho feliz inteiro: catalogo -> produto -> qtd -> carrinho ->
    pagamento -> finalizado, formando um pedido REAL no banco."""

    def test_fluxo_completo_de_compra(self, db, criar_estabelecimento,
                                      criar_cliente, criar_produto):
        estab = criar_estabelecimento(chave_pix="pix@teste.com")
        cliente = criar_cliente(telefone="11999999999")
        criar_produto(estabelecimento_id=estab.id, nome="Picanha",
                      preco=Decimal("59.90"))
        criar_produto(estabelecimento_id=estab.id, nome="Coxinha",
                      preco=Decimal("7.50"), unidade_medida="UNIDADE")

        maquina = MaquinaEstados()
        fluxo = ["1", "1", "1", "1.5", "3", "1"]

        for texto in fluxo:
            maquina.processar(db, estab.id, "11999999999", msg(texto))

        pedido = (
            db.query(Pedido)
            .filter(Pedido.estabelecimento_id == estab.id)
            .order_by(Pedido.id.desc())
            .first()
        )
        assert pedido is not None
        assert pedido.status == "FINALIZADO"
        assert pedido.cliente_id == cliente.id
        assert pedido.valor_total == Decimal("89.85")  # 1.5kg * R$ 59.90
        assert len(pedido.itens) == 1

    def test_sessao_persistida_entre_mensagens(self, db, criar_estabelecimento,
                                               criar_cliente, criar_produto):
        estab = criar_estabelecimento()
        criar_cliente(telefone="11988887777")
        criar_produto(estabelecimento_id=estab.id, nome="Picanha",
                      preco=Decimal("59.90"))

        maquina = MaquinaEstados()
        # cada processar() recarrega a sessao do banco (simula chamadas webhook)
        maquina.processar(db, estab.id, "11988887777", msg("1"))    # menu -> catalogo
        maquina.processar(db, estab.id, "11988887777", msg("1"))    # lista catalogo
        maquina.processar(db, estab.id, "11988887777", msg("1"))    # escolhe produto
        maquina.processar(db, estab.id, "11988887777", msg("1.5"))  # adiciona 1.5kg qtd

        # a sessao foi criada e persiste o estado apos adicionar ao carrinho
        sessao = db.query(ConversaSessao).one()
        assert sessao.estado_atual == "CARRINHO"

    def test_reset_apos_finalizar(self, db, criar_estabelecimento, criar_cliente,
                                  criar_produto):
        estab = criar_estabelecimento()
        criar_cliente(telefone="11977776666")
        criar_produto(estabelecimento_id=estab.id, nome="Picanha",
                      preco=Decimal("59.90"))

        maquina = MaquinaEstados()
        fluxo = ["1", "1", "1", "1.5", "3", "1", "1"]
        for texto in fluxo:
            maquina.processar(db, estab.id, "11977776666", msg(texto))

        # apos finalizar + responder o "novo pedido?", o carrinho esta resetado:
        # tentar finalizar de novo com "3" deve dizer que o carrinho esta vazio
        final = maquina.processar(db, estab.id, "11977776666", msg("3"))
        assert "vazio" in final.lower()

    def test_cliente_nao_cadastrado_recebe_orientacao(self, db,
                                                      criar_estabelecimento):
        estab = criar_estabelecimento()
        maquina = MaquinaEstados()
        resposta = maquina.processar(db, estab.id, "11955550000", msg("1"))
        assert "cadastro" in resposta.lower() or "cadastrado" in resposta.lower()
        # nenhuma sessao criada para quem ainda nao e cliente
        assert db.query(ConversaSessao).count() == 0