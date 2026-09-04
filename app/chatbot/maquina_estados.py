from sqlalchemy.orm import Session

from app.adapters.message_provider import MensagemRecebida
from app.chatbot.contexto import ContextoConversa
from app.chatbot.fabrica_estados import obter_estado
from app.models.conversa_sessao import ConversaSessao
from app.services import cliente_repo


class MaquinaEstados:
    """Carrega/persiste a sessao e delega o processamento ao estado atual."""

    def processar(
        self,
        db: Session,
        estabelecimento_id: int,
        telefone: str,
        mensagem: MensagemRecebida,
    ) -> str:
        cliente = cliente_repo.buscar_cliente_por_telefone(db, telefone)
        if not cliente:
            return (
                "Olá! Você ainda não está cadastrado. "
                "Digite *1* para iniciar o cadastro."
            )

        sessao = self._obter_sessao(db, cliente.id, estabelecimento_id)
        contexto = ContextoConversa.desserializar(sessao.contexto)
        contexto.estabelecimento_id = estabelecimento_id
        contexto.cliente_id = cliente.id

        estado = obter_estado(contexto.estado_atual)
        resposta = estado.handle(contexto, mensagem, db)

        if resposta.novo_estado:
            contexto.estado_atual = resposta.novo_estado
            if resposta.novo_estado == "BEM_VINDO":
                # sessao resetada depois de finalizar/cancelar
                contexto.carrinho = []
                contexto.pedido_id = None
                contexto.produto_aguardando = None
                contexto.produtos_disponiveis = []

        sessao.estado_atual = contexto.estado_atual
        sessao.contexto = contexto.serializar()
        db.commit()

        return resposta.texto

    def _obter_sessao(
        self, db: Session, cliente_id: int, estabelecimento_id: int
    ) -> ConversaSessao:
        sessao = (
            db.query(ConversaSessao)
            .filter(
                ConversaSessao.cliente_id == cliente_id,
                ConversaSessao.estabelecimento_id == estabelecimento_id,
            )
            .first()
        )
        if not sessao:
            sessao = ConversaSessao(
                cliente_id=cliente_id,
                estabelecimento_id=estabelecimento_id,
            )
            db.add(sessao)
            db.flush()
        return sessao
