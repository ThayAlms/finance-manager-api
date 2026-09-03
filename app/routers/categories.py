from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models import Usuario
from app.schemas import CategoriaCreate, CategoriaResponse
from app.services import category as service

router = APIRouter(prefix="/categorias", tags=["Categorias"])


@router.get("", response_model=list[CategoriaResponse], summary="Listar categorias visíveis")
def list_all(
    usuario: Usuario = Depends(get_current_user), session: Session = Depends(get_db)
) -> list[CategoriaResponse]:
    return service.list_all(session, usuario)


@router.get("/{categoria_id}", response_model=CategoriaResponse, summary="Consultar categoria")
def find(
    categoria_id: int,
    usuario: Usuario = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> CategoriaResponse:
    return service.response(service.find(session, categoria_id, usuario))


@router.post("", response_model=CategoriaResponse, status_code=status.HTTP_201_CREATED)
def create(
    request: CategoriaCreate,
    usuario: Usuario = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> CategoriaResponse:
    return service.create(session, usuario, request)


@router.put("/{categoria_id}", response_model=CategoriaResponse)
def update(
    categoria_id: int,
    request: CategoriaCreate,
    usuario: Usuario = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> CategoriaResponse:
    return service.update(session, usuario, categoria_id, request)


@router.delete("/{categoria_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(
    categoria_id: int,
    usuario: Usuario = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> Response:
    service.delete(session, usuario, categoria_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
