from datetime import date

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models import Usuario
from app.schemas import TransacaoCreate, TransacaoResponse
from app.services import transaction as service

router = APIRouter(prefix="/transacoes", tags=["Transações"])


@router.get("", response_model=list[TransacaoResponse], summary="Listar transações por período")
def list_all(
    inicio: date = Query(default=date(1900, 1, 1)),
    fim: date = Query(default=date(2999, 12, 31)),
    usuario: Usuario = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> list[TransacaoResponse]:
    return service.list_all(session, usuario, inicio, fim)


@router.get("/{transacao_id}", response_model=TransacaoResponse)
def find(
    transacao_id: int,
    usuario: Usuario = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> TransacaoResponse:
    return service.response(service.find(session, transacao_id, usuario))


@router.post("", response_model=TransacaoResponse, status_code=status.HTTP_201_CREATED)
def create(
    request: TransacaoCreate,
    usuario: Usuario = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> TransacaoResponse:
    return service.create(session, usuario, request)


@router.put("/{transacao_id}", response_model=TransacaoResponse)
def update(
    transacao_id: int,
    request: TransacaoCreate,
    usuario: Usuario = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> TransacaoResponse:
    return service.update(session, usuario, transacao_id, request)


@router.delete("/{transacao_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(
    transacao_id: int,
    usuario: Usuario = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> Response:
    service.delete(session, usuario, transacao_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
