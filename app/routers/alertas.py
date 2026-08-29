from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import Alerta, Produto
from app.schemas.schemas import AlertaCreate, AlertaOut

router = APIRouter(prefix="/alertas", tags=["alertas"])


@router.post("/", response_model=AlertaOut, status_code=201)
def criar_alerta(alerta: AlertaCreate, db: Session = Depends(get_db)):
    produto = db.query(Produto).filter(Produto.id == alerta.produto_id).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    novo = Alerta(**alerta.model_dump())
    db.add(novo)
    db.commit()
    db.refresh(novo)
    return novo


@router.get("/", response_model=list[AlertaOut])
def listar_alertas(disparado: bool | None = None, db: Session = Depends(get_db)):
    query = db.query(Alerta)
    if disparado is not None:
        query = query.filter(Alerta.disparado == disparado)
    return query.all()
