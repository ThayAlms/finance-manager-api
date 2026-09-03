from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models import Usuario
from app.schemas import UsuarioCreate, UsuarioResponse, UsuarioUpdate
from app.services import user as service

router = APIRouter(prefix="/usuarios", tags=["Usuários"])


@router.post(
    "",
    response_model=UsuarioResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cadastrar usuário",
)
def create(request: UsuarioCreate, session: Session = Depends(get_db)) -> UsuarioResponse:
    return service.create(session, request)


@router.get("/me", response_model=UsuarioResponse, summary="Consultar perfil autenticado")
def get_me(usuario: Usuario = Depends(get_current_user)) -> UsuarioResponse:
    return service.response(usuario)


@router.put("/me", response_model=UsuarioResponse, summary="Atualizar perfil autenticado")
def update_me(
    request: UsuarioUpdate,
    usuario: Usuario = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> UsuarioResponse:
    return service.update(session, usuario, request)
