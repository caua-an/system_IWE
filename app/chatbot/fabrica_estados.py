from app.chatbot.estados_enum import EstadosChatbot
from app.chatbot.interface_estado import Estado
from app.chatbot.estados.bem_vindo import BemVindoEstado
from app.chatbot.estados.carrinho import CarrinhoEstado
from app.chatbot.estados.catalogo import CatalogoEstado
from app.chatbot.estados.pagamento import PagamentoEstado
from app.chatbot.estados.pedido_finalizado import PedidoFinalizadoEstado


_FABRICA: dict[str, type[Estado]] = {
    EstadosChatbot.BEM_VINDO.value: BemVindoEstado,
    EstadosChatbot.CATALOGO.value: CatalogoEstado,
    EstadosChatbot.CARRINHO.value: CarrinhoEstado,
    EstadosChatbot.PAGAMENTO.value: PagamentoEstado,
    EstadosChatbot.PEDIDO_FINALIZADO.value: PedidoFinalizadoEstado,
}


def obter_estado(nome_estado: str) -> Estado:
    return _FABRICA[nome_estado]()
