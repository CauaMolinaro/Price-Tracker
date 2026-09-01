import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import Usuario
from app.security import decodificar_access_token

# tokenUrl aponta pra rota de login — usado só pra gerar a documentação
# interativa do Swagger (o botão "Authorize"), não afeta a validação em si.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> Usuario:
    credenciais_invalidas = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decodificar_access_token(token)
        email: str | None = payload.get("sub")
        if email is None:
            raise credenciais_invalidas
    except jwt.PyJWTError:
        raise credenciais_invalidas

    usuario = db.query(Usuario).filter(Usuario.email == email).first()
    if usuario is None:
        raise credenciais_invalidas

    return usuario