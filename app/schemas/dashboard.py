from datetime import date
from decimal import Decimal

from app.models.enums import Natureza, TipoMovimento
from app.schemas.common import SchemaBase


class ResumoNatureza(SchemaBase):
    natureza: Natureza
    receitas: Decimal
    despesas: Decimal
    resultado: Decimal


class ResumoCategoria(SchemaBase):
    categoria_id: int
    categoria_nome: str
    tipo: TipoMovimento
    total: Decimal


class ResumoMensal(SchemaBase):
    mes: str
    receitas: Decimal
    despesas: Decimal
    resultado: Decimal


class ResumoResponse(SchemaBase):
    inicio: date
    fim: date
    saldo_total: Decimal
    receitas: Decimal
    despesas: Decimal
    resultado: Decimal
    taxa_economia: Decimal
    por_natureza: list[ResumoNatureza]
    por_categoria: list[ResumoCategoria]
    evolucao_mensal: list[ResumoMensal]


class InsightResponse(SchemaBase):
    insight: str
    gerado_por_ia: bool
    modelo: str | None = None
    aviso: str | None = None
