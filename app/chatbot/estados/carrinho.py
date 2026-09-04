from sqlalchemy.orm import Session

from app.adapters.message_provider import MensagemRecebida
from app.chatbot.contexto import ContextoConversa
from app.chatbot.estados_enum import EstadosChatbot
from app.chatbot.interface_estado import Estado, Resposta
from app.schemas.pedido_schema import PedidoCreate, PedidoItemCreate
from app.services import pedido_repo, pedido_item_repo


class CarrinhoEstado(Estado):
    def handle(
        self,
        contexto: ContextoConversa,
        mensagem: MensagemRecebida,
        db,
    ) -> Resposta:
        escolha = (mensagem.texto or "").strip()

        if escolha == "1":
            # voltar ao catalogo
            return Resposta("", novo_estado=EstadosChatbot.CATALOGO.value)

        if escolha == "2":
            return Resposta(self._exibir_carrinho(contexto))

        if escolha == "3":
            if not contexto.carrinho:
                return Resposta(
                    "Seu carrinho está vazio. Responda *1* para ver o catálogo."
                )
            pedido = self._criar_pedido(db, contexto)
            contexto.pedido_id = pedido.id
            return Resposta(
                "Pedido em análise! Segue abaixo os dados para pagamento.",
                novo_estado=EstadosChatbot.PAGAMENTO.value,
            )

        return Resposta(
            self._exibir_carrinho(contexto)
            + "\n\n1 - Continuar comprando\n2 - Ver carrinho\n3 - Finalizar pedido"
        )

    def _exibir_carrinho(self, contexto: ContextoConversa) -> str:
        if not contexto.carrinho:
            return "Seu carrinho está vazio."
        linhas = ["*Seu carrinho:*"]
        for i, item in enumerate(contexto.carrinho, start=1):
            linha = (
                f"{i}. {item['nome']} x{item['quantidade']} "
                f"{item['unidade_medida']} - R$ "
                f"{item['quantidade'] * item['preco_unitario']:.2f}"
            )
            linhas.append(linha)
        linhas.append(f"\n*Total: R$ {contexto.valor_total():.2f}*")
        return "\n".join(linhas)

    def _criar_pedido(self, db: Session, contexto: ContextoConversa):
        pedido = pedido_repo.criar_pedido(
            db,
            PedidoCreate(
                estabelecimento_id=contexto.estabelecimento_id,
                cliente_id=contexto.cliente_id,
            ),
        )
        for item in contexto.carrinho:
            pedido_item_repo.adicionar_item(
                db,
                pedido_id=pedido.id,
                item=PedidoItemCreate(
                    produto_id=item.get("produto_id"),
                    nome=item["nome"],
                    quantidade=item["quantidade"],
                    preco_unitario=item["preco_unitario"],
                    unidade_medida=item["unidade_medida"],
                ),
            )
        return pedido
