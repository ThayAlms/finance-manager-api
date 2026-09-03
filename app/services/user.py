from sqlalchemy.orm import Session

from app.core.errors import conflict
from app.core.security import hash_password
from app.models import Usuario
from app.repositories import user as repository
from app.schemas import UsuarioCreate, UsuarioResponse, UsuarioUpdate


def response(usuario: Usuario) -> UsuarioResponse:
    return UsuarioResponse.model_validate(usuario)


def create(session: Session, request: UsuarioCreate) -> UsuarioResponse:
    email = str(request.email).strip().lower()
    if repository.by_email(session, email):
        conflict("Já existe um usuário cadastrado com este e-mail")
    usuario = Usuario(
        nome=request.nome.strip(),
        email=email,
        senha_hash=hash_password(request.senha),
    )
    return response(repository.save(session, usuario))


def update(
    session: Session, usuario: Usuario, request: UsuarioUpdate
) -> UsuarioResponse:
    email = str(request.email).strip().lower()
    duplicate = repository.by_email(session, email)
    if duplicate is not None and duplicate.id != usuario.id:
        conflict("Já existe um usuário cadastrado com este e-mail")
    usuario.nome = request.nome.strip()
    usuario.email = email
    session.commit()
    session.refresh(usuario)
    return response(usuario)
