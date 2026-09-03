from datetime import date, datetime
from decimal import Decimal

from pydantic import Field

from app.schemas.common import SchemaBase


class MetaCreate(SchemaBase):
    nome: str = Field(min_length=1, max_length=80)
    valor_meta: Decimal = Field(gt=0, decimal_places=2)
    valor_atual: Decimal = Field(default=Decimal("0.00"), ge=0, decimal_places=2)
    prazo: date | None = None


class MetaResponse(SchemaBase):
    id: int
    nome: str
    valor_meta: Decimal
    valor_atual: Decimal
    valor_restante: Decimal
    progresso_percentual: Decimal
    atingida: bool
    prazo: date | None
    criado_em: datetime
