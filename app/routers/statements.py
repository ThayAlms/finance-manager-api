from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models import Usuario
from app.schemas import (
    ExtratoConfirmRequest,
    ExtratoConfirmResponse,
    ExtratoPreviewRequest,
    ExtratoPreviewResponse,
)
from app.services import statement as service

router = APIRouter(prefix="/extratos", tags=["Importação de extratos"])


@router.post(
    "/preview",
    response_model=ExtratoPreviewResponse,
    summary="Analisar extrato sem gravar transações",
)
def preview(
    request: ExtratoPreviewRequest,
    usuario: Usuario = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> ExtratoPreviewResponse:
    return service.preview(session, usuario, request)


@router.post(
    "/confirmar",
    response_model=ExtratoConfirmResponse,
    summary="Confirmar e gravar lançamentos revisados",
)
def confirm(
    request: ExtratoConfirmRequest,
    usuario: Usuario = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> ExtratoConfirmResponse:
    return service.confirm(session, usuario, request)
