from fastapi import APIRouter
from sqlalchemy import text

from app.core.database import DbSession

router = APIRouter(tags=["Saúde"])


@router.get(
    "/health",
    summary="Verificar API e banco",
    description=(
        "Responde `{\"status\": \"UP\"}` quando a API está de pé **e** o "
        "banco responde. A checagem executa um `SELECT 1` real: sem isso o "
        "endpoint responderia UP com o Postgres fora do ar, que é justamente "
        "o cenário que ele deveria denunciar.\n\n"
        "Endpoint público, fora do prefixo `/api/v1`."
    ),
)
@router.get("/actuator/health", include_in_schema=False)
def health(session: DbSession) -> dict[str, str]:
    session.execute(text("SELECT 1"))
    return {"status": "UP"}
