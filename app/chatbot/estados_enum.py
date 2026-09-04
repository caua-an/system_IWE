from enum import Enum


class EstadosChatbot(str, Enum):
    BEM_VINDO = "BEM_VINDO"
    CATALOGO = "CATALOGO"
    CARRINHO = "CARRINHO"
    PAGAMENTO = "PAGAMENTO"
    PEDIDO_FINALIZADO = "PEDIDO_FINALIZADO"
