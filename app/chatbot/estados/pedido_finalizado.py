from app.adapters.message_provider import MensagemRecebida
from app.chatbot.contexto import ContextoConversa
from app.chatbot.estados_enum import EstadosChatbot
from app.chatbot.interface_estado import Estado, Resposta


class PedidoFinalizadoEstado(Estado):
    def handle(
        self,
        contexto: ContextoConversa,
        mensagem: MensagemRecebida,
        db,
    ) -> Resposta:
        return Resposta(
            "Seu pedido foi concluído. Deseja fazer um novo pedido?\n"
            "1 - Sim\n2 - Não",
            novo_estado=EstadosChatbot.BEM_VINDO.value,
        )
