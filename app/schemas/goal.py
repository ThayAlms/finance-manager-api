from datetime import date, datetime
from decimal import Decimal

from pydantic import ConfigDict, Field

from app.schemas.common import SchemaBase


class MetaCreate(SchemaBase):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "nome": "Reserva de impostos",
                "valor_meta": "10000.00",
                "valor_atual": "2500.00",
                "prazo": "2026-12-31",
            }
        }
    )

    nome: str = Field(min_length=1, max_length=80, description="Único por usuário.")
    valor_meta: Decimal = Field(
        gt=0,
        decimal_places=2,
        description="Maior que zero: zero faria o progresso dividir por zero (RN11).",
    )
    valor_atual: Decimal = Field(
        default=Decimal("0.00"),
        ge=0,
        decimal_places=2,
        description="Quanto já foi guardado. Alimentado à mão (R07); pode ultrapassar a meta.",
    )
    prazo: date | None = Field(default=None, description="Opcional.")


class MetaResponse(SchemaBase):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": 1,
                "nome": "Reserva de impostos",
                "valor_meta": "10000.00",
                "valor_atual": "2500.00",
                "valor_restante": "7500.00",
                "progresso_percentual": "25.00",
                "atingida": False,
                "prazo": "2026-12-31",
                "criado_em": "2026-09-07T18:00:00-03:00",
            }
        }
    )

    id: int
    nome: str
    valor_meta: Decimal
    valor_atual: Decimal
    valor_restante: Decimal = Field(description="`max(0, valor_meta − valor_atual)` (RN11).")
    progresso_percentual: Decimal = Field(
        description="`min(100, valor_atual / valor_meta × 100)` (RN11)."
    )
    atingida: bool = Field(description="`valor_atual >= valor_meta` (RN12).")
    prazo: date | None
    criado_em: datetime
