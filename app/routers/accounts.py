from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.core.database import DbSession
from app.core.security import CurrentUser
from app.schemas import ContaCreate, ContaResponse, ContaUpdate
from app.services import account as service

router = APIRouter(prefix="/contas", tags=["Contas"])


@router.get("", response_model=list[ContaResponse], summary="Listar contas e saldos")
def list_all(
    usuario: CurrentUser, session: DbSession
) -> list[ContaResponse]:
    return service.list_all(session, usuario)


@router.get("/{conta_id}", response_model=ContaResponse, summary="Consultar conta e saldo")
def find(
    conta_id: int,
    usuario: CurrentUser,
    session: DbSession,
) -> ContaResponse:
    return service.response(session, service.find(session, conta_id, usuario))


@router.post("", response_model=ContaResponse, status_code=status.HTTP_201_CREATED)
def create(
    request: ContaCreate,
    usuario: CurrentUser,
    session: DbSession,
) -> ContaResponse:
    return service.create(session, usuario, request)


@router.put("/{conta_id}", response_model=ContaResponse)
def update(
    conta_id: int,
    request: ContaUpdate,
    usuario: CurrentUser,
    session: DbSession,
) -> ContaResponse:
    return service.update(session, usuario, conta_id, request)


@router.delete("/{conta_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(
    conta_id: int,
    usuario: CurrentUser,
    session: DbSession,
) -> Response:
    service.delete(session, usuario, conta_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
