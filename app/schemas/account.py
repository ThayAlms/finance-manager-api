from datetime import datetime
from decimal import Decimal

from pydantic import ConfigDict, Field

from app.models.enums import Natureza, TipoConta
from app.schemas.common import SchemaBase


class ContaCreate(SchemaBase):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "nome": "Conta do negócio",
                "tipo": "CORRENTE",
                "natureza": "NEGOCIO",
                "saldo_inicial": "2000.00",
            }
        }
    )

    nome: str = Field(
        min_length=1, max_length=80, description="Único por usuário, ignorando maiúsculas."
    )
    tipo: TipoConta
    natureza: Natureza = Field(
        description="PESSOAL ou NEGOCIO. Obrigatória — é o recorte do produto (RN14)."
    )
    saldo_inicial: Decimal = Field(
        default=Decimal("0.00"),
        decimal_places=2,
        description=(
            "Quanto já havia na conta antes do primeiro lançamento. Só pode "
            "ser definido na criação: alterá-lo depois reescreveria o saldo "
            "retroativamente sem deixar rastro no extrato."
        ),
    )


class ContaUpdate(SchemaBase):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "nome": "Conta do negócio (PJ)",
                "tipo": "CORRENTE",
                "natureza": "NEGOCIO",
            }
        }
    )

    nome: str = Field(min_length=1, max_length=80)
    tipo: TipoConta
    natureza: Natureza


class ContaResponse(SchemaBase):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": 2,
                "nome": "Conta do negócio",
                "tipo": "CORRENTE",
                "natureza": "NEGOCIO",
                "saldo_inicial": "2000.00",
                "saldo_atual": "2800.00",
                "criado_em": "2026-09-07T18:00:00-03:00",
            }
        }
    )

    id: int
    nome: str
    tipo: TipoConta
    natureza: Natureza
    saldo_inicial: Decimal
    saldo_atual: Decimal = Field(
        description=(
            "`saldo_inicial + receitas − despesas` da conta, calculado a cada "
            "leitura (RN07). Não existe coluna `saldo` no banco."
        )
    )
    criado_em: datetime
