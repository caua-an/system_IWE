from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


# contrato neutro de mensagem recebida, moldado pelo payload da Meta Cloud API
@dataclass
class MensagemRecebida:
    remetente: str          # telefone do cliente (from)
    texto: str | None       # conteudo textual (None para midia)
    tipo_mensagem: str      # ex.: "text", "image", "interactive"
    mensagem_id: str        # id unico da mensagem (evita reprocessamento)


# interface que abstrai o provedor de mensageria
class MessageProvider(ABC):
    @abstractmethod
    def enviar_texto(self, destinatario: str, texto: str) -> None:
        ...

    @abstractmethod
    def processar_webhook(self, payload: dict) -> list[MensagemRecebida]:
        ...
