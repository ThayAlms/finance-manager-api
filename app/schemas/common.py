from datetime import datetime

from pydantic import BaseModel, ConfigDict


class SchemaBase(BaseModel):
    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)


class ApiError(BaseModel):
    timestamp: datetime
    status: int
    error: str
    message: str
    path: str
    fieldErrors: dict[str, str] | None = None


COMMON_RESPONSES = {
    400: {"model": ApiError, "description": "JSON malformado"},
    401: {"model": ApiError, "description": "Token ausente, inválido ou expirado"},
    403: {"model": ApiError, "description": "Operação não permitida"},
    404: {"model": ApiError, "description": "Recurso não encontrado"},
    409: {"model": ApiError, "description": "Conflito de estado ou duplicidade"},
    422: {"model": ApiError, "description": "Regra ou campo inválido"},
}
