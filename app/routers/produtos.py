from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.models.models import Produto
from app.schemas.schemas import ProdutoCreate, ProdutoOut, ProdutoComHistorico

router = APIRouter(prefix="/produtos", tags=["produtos"])


@router.post("/", response_model=ProdutoOut, status_code=201)
def criar_produto(produto: ProdutoCreate, db: Session = Depends(get_db)):
    novo = Produto(**produto.model_dump())
    db.add(novo)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Produto com essa URL já cadastrado")
    db.refresh(novo)
    return novo


@router.get("/", response_model=list[ProdutoOut])
def listar_produtos(
    skip: int = 0,
    limit: int = 50,
    loja: str | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(Produto)
    if loja:
        query = query.filter(Produto.loja.ilike(f"%{loja}%"))
    return query.offset(skip).limit(limit).all()


@router.get("/{produto_id}", response_model=ProdutoComHistorico)
def obter_produto(produto_id: int, db: Session = Depends(get_db)):
    produto = db.query(Produto).filter(Produto.id == produto_id).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return produto


@router.delete("/{produto_id}", status_code=204)
def remover_produto(produto_id: int, db: Session = Depends(get_db)):
    produto = db.query(Produto).filter(Produto.id == produto_id).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    db.delete(produto)
    db.commit()
