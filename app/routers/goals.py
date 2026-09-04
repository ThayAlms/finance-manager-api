from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models import Usuario
from app.schemas import MetaCreate, MetaResponse
from app.services import goal as service

router = APIRouter(prefix="/metas", tags=["Metas"])


@router.get("", response_model=list[MetaResponse], summary="Listar metas")
def list_all(
    usuario: Usuario = Depends(get_current_user), session: Session = Depends(get_db)
) -> list[MetaResponse]:
    return service.list_all(session, usuario)


@router.get("/{meta_id}", response_model=MetaResponse)
def find(
    meta_id: int,
    usuario: Usuario = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> MetaResponse:
    return service.response(service.find(session, meta_id, usuario))


@router.post("", response_model=MetaResponse, status_code=status.HTTP_201_CREATED)
def create(
    request: MetaCreate,
    usuario: Usuario = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> MetaResponse:
    return service.create(session, usuario, request)


@router.put("/{meta_id}", response_model=MetaResponse)
def update(
    meta_id: int,
    request: MetaCreate,
    usuario: Usuario = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> MetaResponse:
    return service.update(session, usuario, meta_id, request)


@router.delete("/{meta_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(
    meta_id: int,
    usuario: Usuario = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> Response:
    service.delete(session, usuario, meta_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
