from sqlalchemy.orm import Session

from app.adapters.message_provider import MensagemRecebida
from app.chatbot.contexto import ContextoConversa
from app.chatbot.estados_enum import EstadosChatbot
from app.chatbot.interface_estado import Estado, Resposta
from app.models.produto import Produto


class CatalogoEstado(Estado):
    def handle(
        self,
        contexto: ContextoConversa,
        mensagem: MensagemRecebida,
        db,
    ) -> Resposta:
        texto = (mensagem.texto or "").strip()

        # ainda nao escolheu produto -> busca um catalogo
        if contexto.produto_aguardando is None:
            produtos = (
                db.query(Produto)
                .filter(
                    Produto.estabelecimento_id == contexto.estabelecimento_id,
                    Produto.ativo.is_(True),
                )
                .all()
            )
            if not produtos:
                return Resposta(
                    "Ainda não temos produtos cadastrados. Volte mais tarde.",
                    novo_estado=EstadosChatbot.BEM_VINDO.value,
                )

            linhas = ["*Catálogo:*\n"]
            for idx, prod in enumerate(produtos, start=1):
                linhas.append(
                    f"{idx}. {prod.nome} - R$ {prod.preco:.2f} /{prod.unidade_medida}"
                )
            linhas.append("\nResponda com o número do produto e depois a quantidade.")

            contexto.produtos_disponiveis = [
                {"id": p.id, "nome": p.nome, "preco": float(p.preco), "unidade": p.unidade_medida}
                for p in produtos
            ]
            contexto.produto_aguardando = {}
            return Resposta("\n".join(linhas))

        # produto escolhido -> aguarda a quantidade
        if contexto.produto_aguardando == {}:
            if not texto.isdigit():
                return Resposta("Responda com o número de um produto do catálogo.")

            indice = int(texto) - 1
            if indice < 0 or indice >= len(contexto.produtos_disponiveis):
                return Resposta("Opção inválida. Responda com o número de um produto.")
            contexto.produto_aguardando = contexto.produtos_disponiveis[indice]
            return Resposta(
                f"Quantos kg/unidades de *{contexto.produto_aguardando['nome']}*? "
                "Responda apenas o número."
            )

        # recebe a quantidade
        try:
            quantidade = float(texto.replace(",", "."))
        except ValueError:
            return Resposta("Quantidade inválida. Responda apenas o número.")
        if quantidade <= 0:
            return Resposta("A quantidade deve ser maior que zero.")

        dados = contexto.produto_aguardando
        contexto.carrinho.append(
            {
                "produto_id": dados["id"],
                "nome": dados["nome"],
                "quantidade": quantidade,
                "preco_unitario": dados["preco"],
                "unidade_medida": dados["unidade"],
            }
        )

        contexto.produto_aguardando = None
        contexto.produtos_disponiveis = []
        return Resposta(
            f"*{dados['nome']}* adicionado ao carrinho! 🛒\n\n"
            "1 - Continuar comprando\n"
            "2 - Ver carrinho\n"
            "3 - Finalizar pedido",
            novo_estado=EstadosChatbot.CARRINHO.value,
        )
