from datetime import date, datetime
from decimal import Decimal

from pydantic import Field

from app.models.enums import Natureza, TipoMovimento
from app.schemas.common import SchemaBase


class TransacaoCreate(SchemaBase):
    conta_id: int
    categoria_id: int
    descricao: str = Field(min_length=1, max_length=160)
    valor: Decimal = Field(gt=0, decimal_places=2)
    data: date
    tipo: TipoMovimento
    natureza: Natureza | None = None


class TransacaoResponse(SchemaBase):
    id: int
    conta_id: int
    conta_nome: str
    categoria_id: int
    categoria_nome: str
    descricao: str
    valor: Decimal
    data: date
    tipo: TipoMovimento
    natureza: Natureza
    criado_em: datetime
