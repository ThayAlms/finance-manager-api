from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models import Usuario
from app.schemas.dashboard import ResumoResponse
from app.services import dashboard as service

router = APIRouter(prefix="/resumo", tags=["Dashboard"])


@router.get("", response_model=ResumoResponse, summary="Consultar resumo financeiro")
def summary(
    inicio: date = Query(...),
    fim: date = Query(...),
    usuario: Usuario = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> ResumoResponse:
    return service.summary(session, usuario, inicio, fim)
