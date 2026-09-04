from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import DbSession
from app.core.security import CurrentUser
from app.schemas import UsuarioCreate, UsuarioResponse, UsuarioUpdate
from app.services import user as service

router = APIRouter(prefix="/usuarios", tags=["Usuários"])


@router.post(
    "",
    response_model=UsuarioResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cadastrar usuário",
)
def create(request: UsuarioCreate, session: DbSession) -> UsuarioResponse:
    return service.create(session, request)


@router.get("/me", response_model=UsuarioResponse, summary="Consultar perfil autenticado")
def get_me(usuario: CurrentUser) -> UsuarioResponse:
    return service.response(usuario)


@router.put("/me", response_model=UsuarioResponse, summary="Atualizar perfil autenticado")
def update_me(
    request: UsuarioUpdate,
    usuario: CurrentUser,
    session: DbSession,
) -> UsuarioResponse:
    return service.update(session, usuario, request)
