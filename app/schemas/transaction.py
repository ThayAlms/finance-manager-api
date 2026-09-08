from datetime import date, datetime
from decimal import Decimal

from pydantic import ConfigDict, Field

from app.models.enums import Natureza, TipoMovimento
from app.schemas.common import SchemaBase


class TransacaoCreate(SchemaBase):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "conta_id": 1,
                "categoria_id": 4,
                "descricao": "Combustível para entrega do cliente",
                "valor": "100.00",
                "data": "2026-09-07",
                "tipo": "DESPESA",
                "natureza": "NEGOCIO",
            }
        }
    )

    conta_id: int = Field(description="Precisa ser uma conta do usuário do token (RN06).")
    categoria_id: int = Field(
        description="Categoria de sistema ou do próprio usuário, do mesmo `tipo` (RN05 e RN06)."
    )
    descricao: str = Field(min_length=1, max_length=160)
    valor: Decimal = Field(
        gt=0,
        decimal_places=2,
        description=(
            "Sempre positivo (RN04). Quem decide se soma ou subtrai é o "
            "`tipo`, nunca o sinal do valor."
        ),
    )
    data: date = Field(description="Não pode ser futura (RN13).")
    tipo: TipoMovimento = Field(description="Precisa ser igual ao tipo da categoria (RN05).")
    natureza: Natureza | None = Field(
        default=None,
        description=(
            "Opcional: omitida, herda a natureza da conta (RN14). Informe-a "
            "para registrar o caso que o produto existe para resolver — a "
            "despesa do negócio paga pela conta pessoal."
        ),
    )


class TransacaoResponse(SchemaBase):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": 12,
                "conta_id": 1,
                "conta_nome": "Conta pessoal",
                "categoria_id": 4,
                "categoria_nome": "Combustível",
                "descricao": "Combustível para entrega do cliente",
                "valor": "100.00",
                "data": "2026-09-07",
                "tipo": "DESPESA",
                "natureza": "NEGOCIO",
                "criado_em": "2026-09-07T18:00:00-03:00",
            }
        }
    )

    id: int
    conta_id: int
    conta_nome: str = Field(description="Devolvido junto para o extrato não precisar de N+1 chamadas.")
    categoria_id: int
    categoria_nome: str
    descricao: str
    valor: Decimal
    data: date
    tipo: TipoMovimento
    natureza: Natureza
    criado_em: datetime
