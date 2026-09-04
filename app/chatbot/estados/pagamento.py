from app.adapters.message_provider import MensagemRecebida
from app.chatbot.contexto import ContextoConversa
from app.chatbot.estados_enum import EstadosChatbot
from app.chatbot.interface_estado import Estado, Resposta
from app.services import estabelecimento_repo, pedido_repo


class PagamentoEstado(Estado):
    def handle(
        self,
        contexto: ContextoConversa,
        mensagem: MensagemRecebida,
        db,
    ) -> Resposta:
        texto = (mensagem.texto or "").strip()

        if texto == "1":
            # confirma pagamento -> finaliza o pedido
            if contexto.pedido_id:
                pedido = pedido_repo.buscar_pedido(
                    db, contexto.pedido_id, contexto.estabelecimento_id
                )
                if pedido and pedido.status == "ABERTO":
                    pedido_repo.atualizar_status(db, pedido, "FINALIZADO")
            return Resposta(
                "Pedido finalizado! Agradecemos a preferência. 🎉",
                novo_estado=EstadosChatbot.PEDIDO_FINALIZADO.value,
            )

        if texto == "2":
            return Resposta(
                "Pedido cancelado. Até a próxima!",
                novo_estado=EstadosChatbot.BEM_VINDO.value,
            )

        return Resposta(self._montar_pagamento(db, contexto))

    def _montar_pagamento(self, db, contexto: ContextoConversa) -> str:
        estab = estabelecimento_repo.buscar_estabelecimento_id(
            db, contexto.estabelecimento_id
        )
        chave_pix = estab.chave_pix if estab else None
        linhas = [
            "*Pagamento via PIX*",
            f"Total a pagar: *R$ {contexto.valor_total():.2f}*",
        ]
        if chave_pix:
            linhas.append(f"\nChave PIX: `{chave_pix}`")
        linhas.append(
            "\nApós realizar o pagamento, responda:\n"
            "1 - Já paguei\n"
            "2 - Cancelar pedido"
        )
        return "\n".join(linhas)
