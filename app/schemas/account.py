from datetime import datetime
from decimal import Decimal

from pydantic import Field

from app.models.enums import Natureza, TipoConta
from app.schemas.common import SchemaBase


class ContaCreate(SchemaBase):
    nome: str = Field(min_length=1, max_length=80)
    tipo: TipoConta
    natureza: Natureza
    saldo_inicial: Decimal = Field(default=Decimal("0.00"), decimal_places=2)


class ContaUpdate(SchemaBase):
    nome: str = Field(min_length=1, max_length=80)
    tipo: TipoConta
    natureza: Natureza


class ContaResponse(SchemaBase):
    id: int
    nome: str
    tipo: TipoConta
    natureza: Natureza
    saldo_inicial: Decimal
    saldo_atual: Decimal
    criado_em: datetime
