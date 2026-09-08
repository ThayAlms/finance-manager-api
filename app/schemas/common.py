from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class SchemaBase(BaseModel):
    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)


class ApiError(BaseModel):
    """Corpo unico de erro da API. Toda falha responde neste formato."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "timestamp": "2026-09-07T18:00:00+00:00",
                "status": 422,
                "error": "Unprocessable Entity",
                "message": "A data da transação não pode estar no futuro",
                "path": "/api/v1/transacoes",
            }
        }
    )

    timestamp: datetime
    status: int
    error: str
    message: str
    path: str
    fieldErrors: dict[str, str] | None = Field(
        default=None,
        description=(
            "Presente apenas em falhas de validação de campo: mapeia o campo "
            "para o motivo da recusa."
        ),
    )


COMMON_RESPONSES = {
    400: {"model": ApiError, "description": "JSON malformado"},
    401: {"model": ApiError, "description": "Token ausente, inválido ou expirado"},
    403: {"model": ApiError, "description": "Operação não permitida"},
    404: {"model": ApiError, "description": "Recurso não encontrado"},
    409: {"model": ApiError, "description": "Conflito de estado ou duplicidade"},
    422: {"model": ApiError, "description": "Regra ou campo inválido"},
}
