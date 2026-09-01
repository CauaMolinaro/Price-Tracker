from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.models import Alerta, Produto, Usuario
from app.schemas.schemas import AlertaCreate, AlertaOut

router = APIRouter(prefix="/alertas", tags=["alertas"])


@router.post("/", response_model=AlertaOut, status_code=201)
def criar_alerta(
    alerta: AlertaCreate,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(get_current_user),
):
    produto = db.query(Produto).filter(Produto.id == alerta.produto_id).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    novo = Alerta(**alerta.model_dump(), usuario_id=usuario_atual.id)
    db.add(novo)
    db.commit()
    db.refresh(novo)
    return novo


@router.get("/", response_model=list[AlertaOut])
def listar_meus_alertas(
    disparado: bool | None = None,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(get_current_user),
):
    """Lista apenas os alertas do usuário autenticado."""
    query = db.query(Alerta).filter(Alerta.usuario_id == usuario_atual.id)
    if disparado is not None:
        query = query.filter(Alerta.disparado == disparado)
    return query.all()