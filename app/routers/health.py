from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import DbSession

router = APIRouter(tags=["Saúde"])


@router.get("/health", summary="Verificar API e banco")
@router.get("/actuator/health", include_in_schema=False)
def health(session: DbSession) -> dict[str, str]:
    session.execute(text("SELECT 1"))
    return {"status": "UP"}
