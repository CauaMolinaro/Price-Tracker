"""
Utilitários de autenticação: hash de senha e tokens JWT.
"""
import os
from datetime import datetime, timedelta, timezone

import jwt
from pwdlib import PasswordHash

SECRET_KEY = os.getenv("SECRET_KEY", "chave-secreta-apenas-para-desenvolvimento-local")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))  # 24h

password_hash = PasswordHash.recommended()


def hash_senha(senha: str) -> str:
    return password_hash.hash(senha)


def verificar_senha(senha: str, senha_hash: str) -> bool:
    return password_hash.verify(senha, senha_hash)


def criar_access_token(dados: dict, expira_em: timedelta | None = None) -> str:
    payload = dados.copy()
    expira = datetime.now(timezone.utc) + (
        expira_em or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    payload.update({"exp": expira})
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decodificar_access_token(token: str) -> dict:
    """Lança jwt.PyJWTError se o token for inválido ou tiver expirado."""
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])