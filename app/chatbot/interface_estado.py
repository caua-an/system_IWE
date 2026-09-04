from __future__ import annotations

from abc import ABC, abstractmethod

from app.adapters.message_provider import MensagemRecebida
from app.chatbot.contexto import ContextoConversa


class Resposta:
    def __init__(self, texto: str, novo_estado: str | None = None):
        self.texto = texto
        self.novo_estado = novo_estado  # None => permanece no estado atual


# cada estado do chatbot implementa este contrato.
# recebe o contexto atual, a mensagem e ferramentas de consulta (db), e devolve
# um texto de resposta e a transicao de estado.
class Estado(ABC):
    @abstractmethod
    def handle(
        self,
        contexto: ContextoConversa,
        mensagem: MensagemRecebida,
        db,
    ) -> Resposta:
        ...
