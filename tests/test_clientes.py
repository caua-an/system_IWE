import pytest
from pydantic import ValidationError

from app.schemas.cliente_schema import ClienteCreate, ClienteUpdate
from app.services import cliente_repo


# ---------------------------------------------------------------------------
# SCHEMA -> REPO -> API, um dominio completo por arquivo.
# O schema prova o fail-fast antes do banco; a API prova o contrato completo.
# ---------------------------------------------------------------------------

class TestClienteSchema:
    def test_telefone_valido_no_range(self):
        ClienteCreate(telefone="11999999999")
        ClienteCreate(telefone="1" * 10)
        ClienteCreate(telefone="1" * 20)

    def test_telefone_curto_demais(self):
        with pytest.raises(ValidationError):
            ClienteCreate(telefone="123")

    def test_telefone_longo_demais(self):
        with pytest.raises(ValidationError):
            ClienteCreate(telefone="1" * 25)

    def test_telefone_obrigatorio(self):
        with pytest.raises(ValidationError):
            ClienteCreate()


class TestClienteRepo:
    def test_criar_cliente_apenas_com_telefone(self, db):
        # o chatbot salva primeiro so o numero; nome/endereco vao depois
        cliente = cliente_repo.criar_Cliente(db, ClienteCreate(telefone="11988887777"))
        assert cliente.id is not None
        assert cliente.nome is None
        assert cliente.endereco_entrega is None

    def test_buscar_por_telefone_e_por_id(self, db):
        criado = cliente_repo.criar_Cliente(db, ClienteCreate(telefone="11977776666"))
        assert cliente_repo.buscar_cliente_por_telefone(db, "11977776666").id == criado.id
        assert cliente_repo.buscar_cliente_por_id(db, criado.id).id == criado.id
        assert cliente_repo.buscar_cliente_por_telefone(db, "11900000000") is None

    def test_atualizar_preenche_nome_e_endereco(self, db):
        # REGRESSAO: antigamente gravava em atributo inexistente "endereco"
        # (AttributeError silencioso). Agora usa endereco_entrega, coluna real.
        criado = cliente_repo.criar_Cliente(db, ClienteCreate(telefone="11966665555"))
        atualizado = cliente_repo.atualizar_cliente(
            db,
            cliente_id=criado.id,
            dados=ClienteUpdate(
                telefone="11966665555",
                nome="Maria",
                endereco_entrega="Rua A, 10",
            ),
        )
        assert atualizado.nome == "Maria"
        assert atualizado.endereco_entrega == "Rua A, 10"


class TestClienteAPI:
    def test_cadastrar_cliente_com_sucesso(self, client):
        resp = client.post("/clientes/", json={"telefone": "11955554444"})
        assert resp.status_code == 201
        assert resp.json()["telefone"] == "11955554444"

    def test_telefone_duplicado_retorna_400(self, client):
        client.post("/clientes/", json={"telefone": "11933332222"})
        resp = client.post("/clientes/", json={"telefone": "11933332222"})
        assert resp.status_code == 400

    def test_telefone_invalido_retorna_422(self, client):
        resp = client.post("/clientes/", json={"telefone": "123"})
        assert resp.status_code == 422

    def test_buscar_cliente_pelo_telefone(self, client):
        client.post("/clientes/", json={"telefone": "11911112222"})
        resp = client.get("/clientes/11911112222")
        assert resp.status_code == 200
        assert resp.json()["telefone"] == "11911112222"

    def test_buscar_cliente_inexistente_retorna_404(self, client):
        resp = client.get("/clientes/11999998888")
        assert resp.status_code == 404

    def test_atualizar_dados_completos(self, client):
        # REGRESSAO via API: o PATCH deve persistir em endereco_entrega
        criado = client.post("/clientes/", json={"telefone": "11900001111"}).json()
        resp = client.patch(
            f"/clientes/{criado['id']}",
            json={
                "telefone": "11900001111",
                "nome": "Joao",
                "endereco_entrega": "Rua B, 22",
            },
        )
        assert resp.status_code == 200
        assert resp.json()["nome"] == "Joao"
        assert resp.json()["endereco_entrega"] == "Rua B, 22"