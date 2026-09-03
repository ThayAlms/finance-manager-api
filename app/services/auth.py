from sqlalchemy.orm import Session

from app.core.errors import ApiException
from app.core.security import create_access_token, verify_password
from app.repositories import user as user_repository
from app.schemas import LoginRequest, TokenResponse


def login(session: Session, request: LoginRequest) -> TokenResponse:
    email = str(request.email).strip().lower()
    usuario = user_repository.by_email(session, email)
    if usuario is None or not verify_password(request.senha, usuario.senha_hash):
        raise ApiException(401, "E-mail ou senha inválidos")
    return TokenResponse(access_token=create_access_token(usuario.id))
