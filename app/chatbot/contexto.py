from __future__ import annotations

import json


# estado transitivo da conversa, mantido entre mensagens (persistido como JSON)
class ContextoConversa:
    def __init__(
        self,
        estado_atual: str = "BEM_VINDO",
        estabelecimento_id: int | None = None,
        cliente_id: int | None = None,
        carrinho: list | None = None,
        produto_aguardando: dict | None = None,
        produtos_disponiveis: list | None = None,
        pedido_id: int | None = None,
    ):
        self.estado_atual = estado_atual
        self.estabelecimento_id = estabelecimento_id
        self.cliente_id = cliente_id
        self.carrinho: list = carrinho or []
        self.produto_aguardando: dict | None = produto_aguardando
        self.produtos_disponiveis: list = produtos_disponiveis or []
        self.pedido_id: int | None = pedido_id

    def serializar(self) -> str:
        return json.dumps(self.__dict__)

    @classmethod
    def desserializar(cls, texto: str | None) -> "ContextoConversa":
        if not texto:
            return cls()
        dados = json.loads(texto)
        return cls(**dados)

    @property
    def carrinho_cheio(self) -> bool:
        return len(self.carrinho) > 0

    def valor_total(self) -> float:
        return round(
            sum(i["quantidade"] * i["preco_unitario"] for i in self.carrinho), 2
        )
