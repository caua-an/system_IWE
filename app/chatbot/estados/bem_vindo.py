from app.adapters.message_provider import MensagemRecebida
from app.chatbot.contexto import ContextoConversa
from app.chatbot.interface_estado import Estado, Resposta
from app.chatbot.estados_enum import EstadosChatbot


MENU = (
    "*Olá! Bem-vindo(a)!* Escolha uma opção:\n"
    "1 - Ver catálogo\n"
    "2 - Ver meu carrinho\n"
    "3 - Finalizar pedido"
)


class BemVindoEstado(Estado):
    def handle(
        self,
        contexto: ContextoConversa,
        mensagem: MensagemRecebida,
        db,
    ) -> Resposta:
        escolha = (mensagem.texto or "").strip()

        if escolha == "1":
            return Resposta("", novo_estado=EstadosChatbot.CATALOGO.value)

        if escolha == "2" or escolha == "3":
            if not contexto.carrinho:
                return Resposta(
                    "Seu carrinho está vazio. Responda *1* para ver o catálogo.\n\n" + MENU
                )
            if escolha == "2":
                return Resposta(
                    _formatar_carrinho(contexto) + "\n\n" + MENU,
                    novo_estado=EstadosChatbot.CARRINHO.value,
                )
            return Resposta("", novo_estado=EstadosChatbot.CARRINHO.value)

        return Resposta(MENU)


def _formatar_carrinho(contexto: ContextoConversa) -> str:
    if not contexto.carrinho:
        return "Seu carrinho está vazio."
    linhas = ["*Seu carrinho:*"]
    for i, item in enumerate(contexto.carrinho, start=1):
        linhas.append(
            f"{i}. {item.nome} x{item.quantidade} {item.unidade_medida} "
            f"- R$ {item.preco_unitario * item.quantidade:.2f}"
        )
    linhas.append(f"\n*Total: R$ {contexto.valor_total():.2f}*")
    return "\n".join(linhas)
