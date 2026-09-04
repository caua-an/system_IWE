from __future__ import annotations

import requests

from app.adapters.message_provider import MessageProvider, MensagemRecebida


# adapter concreto para a Evolution API (broker de teste).
# O contrato (MensagemRecebida/MessageProvider) espelha a Meta,
# entao a Evolution e normalizada POR TRAS dessa interface.
class EvolutionProvider(MessageProvider):
    def __init__(self, base_url: str, api_key: str, instance: str):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.instance = instance

    def _headers(self) -> dict:
        return {"apikey": self.api_key}

    def enviar_texto(self, destinatario: str, texto: str) -> None:
        url = f"{self.base_url}/message/sendText/{self.instance}"
        body = {"number": destinatario, "textMessage": {"text": texto}}
        requests.post(url, json=body, headers=self._headers(), timeout=10)

    def processar_webhook(self, payload: dict) -> list[MensagemRecebida]:
        mensagens: list[MensagemRecebida] = []
        for evento in payload.get("data", []):
            remetente = evento.get("key", {}).get("remoteJid", "").split("@")[0]
            message = evento.get("message", {})
            texto = None
            tipo = "text"
            if "conversation" in message:
                texto = message["conversation"]
            elif "extendedTextMessage" in message:
                texto = message["extendedTextMessage"].get("text")
            mensagens.append(
                MensagemRecebida(
                    remetente=remetente,
                    texto=texto,
                    tipo_mensagem=tipo,
                    mensagem_id=evento.get("key", {}).get("id", ""),
                )
            )
        return mensagens
