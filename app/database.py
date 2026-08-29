"""
Configuração da conexão com o banco de dados usando SQLAlchemy.

Por padrão usa SQLite (arquivo local) para facilitar rodar o projeto
sem precisar instalar nada além das dependências Python. Para produção,
basta trocar DATABASE_URL para uma string de conexão PostgreSQL, por
exemplo: postgresql://usuario:senha@localhost:5432/price_tracker
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./price_tracker.db")

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependency do FastAPI: abre uma sessão e garante que ela é fechada."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
