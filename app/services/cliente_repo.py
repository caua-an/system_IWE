from sqlalchemy.orm import Session
from app.models.cliente import Cliente
from app.schemas.cliente_schema import ClienteCreate, ClienteUpdate

def criar_Cliente(db: Session, cliente: ClienteCreate):
    db_cliente = Cliente(telefone=cliente.telefone)
    db.add(db_cliente)
    db.commit()
    db.refresh(db_cliente)
    return db_cliente

def buscar_cliente_por_telefone(db: Session, telefone: str):
    return db.query(Cliente).filter(Cliente.telefone == telefone).first()

def buscar_cliente_por_id(db: Session, cliente_id: int):
    return db.query(Cliente).filter(Cliente.id == cliente_id).first()

# primeiramente, o chatbot vai salvar apenas o numero, depois, sera atualizado com outros dados
def atualizar_cliente(db: Session, cliente_id: int, dados: ClienteUpdate):
    db_cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()

    if not db_cliente:
        return None

    if dados.nome is not None:
        db_cliente.nome = dados.nome
    if dados.endereco_entrega is not None:
        db_cliente.endereco_entrega = dados.endereco_entrega

    db.commit()
    db.refresh(db_cliente)
    return db_cliente

    