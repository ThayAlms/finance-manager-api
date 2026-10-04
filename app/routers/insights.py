from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models import Usuario
from app.schemas.dashboard import InsightResponse
from app.services import dashboard, insight

router = APIRouter(prefix="/insights", tags=["Inteligência Artificial"])


@router.post("", response_model=InsightResponse, summary="Gerar análise financeira educativa")
def generate(
    inicio: date = Query(...),
    fim: date = Query(...),
    usuario: Usuario = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> InsightResponse:
    return insight.generate(dashboard.summary(session, usuario, inicio, fim))
