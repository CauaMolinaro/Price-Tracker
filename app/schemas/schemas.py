"""
Schemas Pydantic: definem o formato dos dados que entram e saem da API.
Mantidos separados dos modelos SQLAlchemy (boa prática: não expor o
modelo de banco diretamente na API).
"""
from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict


# ---------- Produto ----------

class ProdutoBase(BaseModel):
    nome: str
    url: str
    loja: str


class ProdutoCreate(ProdutoBase):
    pass


class ProdutoOut(ProdutoBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    criado_em: datetime


# ---------- Histórico de preço ----------

class HistoricoPrecoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    preco: float
    coletado_em: datetime


class ProdutoComHistorico(ProdutoOut):
    historico: list[HistoricoPrecoOut] = []


# ---------- Alerta ----------

class AlertaCreate(BaseModel):
    produto_id: int
    preco_alvo: float
    email: EmailStr


class AlertaOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    produto_id: int
    preco_alvo: float
    email: EmailStr
    disparado: bool
    criado_em: datetime
