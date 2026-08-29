"""
Endpoints relacionados a preços e análises.

Aqui ficam as queries mais "ricas" do projeto — bom lugar pra mostrar
domínio de SQL além do CRUD básico (agregações, joins, filtros por data).
"""
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import Produto, HistoricoPreco
from app.schemas.schemas import HistoricoPrecoOut

router = APIRouter(prefix="/precos", tags=["precos"])


@router.post("/{produto_id}", response_model=HistoricoPrecoOut, status_code=201)
def registrar_preco(produto_id: int, preco: float, db: Session = Depends(get_db)):
    """Registra uma nova coleta de preço para um produto (usado pelo scraper)."""
    produto = db.query(Produto).filter(Produto.id == produto_id).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    registro = HistoricoPreco(produto_id=produto_id, preco=preco)
    db.add(registro)
    db.commit()
    db.refresh(registro)
    return registro


@router.get("/{produto_id}/historico", response_model=list[HistoricoPrecoOut])
def historico_produto(
    produto_id: int, dias: int = 30, db: Session = Depends(get_db)
):
    """Retorna o histórico de preços de um produto nos últimos N dias."""
    limite = datetime.utcnow() - timedelta(days=dias)
    registros = (
        db.query(HistoricoPreco)
        .filter(
            HistoricoPreco.produto_id == produto_id,
            HistoricoPreco.coletado_em >= limite,
        )
        .order_by(HistoricoPreco.coletado_em.asc())
        .all()
    )
    return registros


@router.get("/maiores-quedas")
def maiores_quedas(dias: int = 30, limite: int = 10, db: Session = Depends(get_db)):
    """
    Ranking dos produtos com maior queda percentual de preço no período.

    Query de agregação: para cada produto, compara o preço mais antigo
    com o mais recente dentro da janela de tempo pedida.
    """
    desde = datetime.utcnow() - timedelta(days=dias)

    subquery_primeiro = (
        db.query(
            HistoricoPreco.produto_id,
            func.min(HistoricoPreco.coletado_em).label("data_min"),
        )
        .filter(HistoricoPreco.coletado_em >= desde)
        .group_by(HistoricoPreco.produto_id)
        .subquery()
    )

    subquery_ultimo = (
        db.query(
            HistoricoPreco.produto_id,
            func.max(HistoricoPreco.coletado_em).label("data_max"),
        )
        .filter(HistoricoPreco.coletado_em >= desde)
        .group_by(HistoricoPreco.produto_id)
        .subquery()
    )

    preco_inicial = (
        db.query(HistoricoPreco.produto_id, HistoricoPreco.preco.label("preco_inicial"))
        .join(
            subquery_primeiro,
            (HistoricoPreco.produto_id == subquery_primeiro.c.produto_id)
            & (HistoricoPreco.coletado_em == subquery_primeiro.c.data_min),
        )
        .subquery()
    )

    preco_final = (
        db.query(HistoricoPreco.produto_id, HistoricoPreco.preco.label("preco_final"))
        .join(
            subquery_ultimo,
            (HistoricoPreco.produto_id == subquery_ultimo.c.produto_id)
            & (HistoricoPreco.coletado_em == subquery_ultimo.c.data_max),
        )
        .subquery()
    )

    resultados = (
        db.query(
            Produto.id,
            Produto.nome,
            preco_inicial.c.preco_inicial,
            preco_final.c.preco_final,
        )
        .join(preco_inicial, Produto.id == preco_inicial.c.produto_id)
        .join(preco_final, Produto.id == preco_final.c.produto_id)
        .all()
    )

    ranking = []
    for produto_id, nome, inicial, final in resultados:
        if inicial and inicial > 0:
            variacao_pct = ((final - inicial) / inicial) * 100
            ranking.append(
                {
                    "produto_id": produto_id,
                    "nome": nome,
                    "preco_inicial": inicial,
                    "preco_atual": final,
                    "variacao_percentual": round(variacao_pct, 2),
                }
            )

    ranking.sort(key=lambda x: x["variacao_percentual"])
    return ranking[:limite]
