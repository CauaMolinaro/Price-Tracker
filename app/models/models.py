"""
Modelagem do banco de dados.

Tabelas:
- usuarios: contas com login (email + senha com hash)
- produtos: item que está sendo monitorado (ex: "RTX 4070", "Jogo X na Steam")
- historico_precos: um registro por coleta de preço (série histórica)
- alertas: preço-alvo definido por um usuário para receber notificação

Relacionamento:
usuario (1) -----< (N) alertas
produto (1) -----< (N) historico_precos
produto (1) -----< (N) alertas
"""
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from app.database import Base


def agora_utc():
    """Retorna a hora atual em UTC (substitui datetime.utcnow(), obsoleto)."""
    return datetime.now(timezone.utc)


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), nullable=False, unique=True, index=True)
    senha_hash = Column(String(255), nullable=False)
    criado_em = Column(DateTime, default=agora_utc)

    alertas = relationship(
        "Alerta", back_populates="usuario", cascade="all, delete-orphan"
    )


class Produto(Base):
    __tablename__ = "produtos"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(255), nullable=False, index=True)
    url = Column(String(500), nullable=False, unique=True)
    loja = Column(String(100), nullable=False)  # ex: "Kabum", "Steam"
    criado_em = Column(DateTime, default=agora_utc)

    historico = relationship(
        "HistoricoPreco", back_populates="produto", cascade="all, delete-orphan"
    )
    alertas = relationship(
        "Alerta", back_populates="produto", cascade="all, delete-orphan"
    )


class HistoricoPreco(Base):
    __tablename__ = "historico_precos"

    id = Column(Integer, primary_key=True, index=True)
    produto_id = Column(Integer, ForeignKey("produtos.id"), nullable=False)
    preco = Column(Float, nullable=False)
    coletado_em = Column(DateTime, default=agora_utc, index=True)

    produto = relationship("Produto", back_populates="historico")


class Alerta(Base):
    __tablename__ = "alertas"

    id = Column(Integer, primary_key=True, index=True)
    produto_id = Column(Integer, ForeignKey("produtos.id"), nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    preco_alvo = Column(Float, nullable=False)
    email = Column(String(255), nullable=False)  # e-mail de destino da notificação
    disparado = Column(Boolean, default=False)
    criado_em = Column(DateTime, default=agora_utc)

    produto = relationship("Produto", back_populates="alertas")
    usuario = relationship("Usuario", back_populates="alertas")