from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# A string de conexão reflete as credenciais do seu docker-compose.yml
# Formato: dialect+driver://username:password@host:port/database
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://acougue_user:acougue_password@127.0.0.1:3306/acougue_db"

# O 'engine' é o motor que gerencia o pool de conexões com o MySQL
engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True)

# SessionLocal é a fábrica (Factory Pattern) de sessões de banco
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Classe Base que todos os nossos modelos (tabelas) vão herdar
Base = declarative_base()

# Dependência do FastAPI para injetar a sessão do banco nas rotas de forma segura
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()