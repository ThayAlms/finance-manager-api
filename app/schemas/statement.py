from datetime import date
from decimal import Decimal
from typing import Literal

from pydantic import Field

from app.models.enums import Natureza, TipoConta, TipoMovimento
from app.schemas.common import SchemaBase


class ExtratoPreviewRequest(SchemaBase):
    arquivo_nome: str = Field(min_length=1, max_length=255)
    conteudo: str = Field(min_length=1, max_length=14_000_000)
    codificacao: Literal["texto", "base64"] = "texto"
    conta_nome: str = Field(min_length=1, max_length=80)
    tipo_conta: TipoConta = TipoConta.CORRENTE
    natureza_padrao: Natureza = Natureza.PESSOAL


class LancamentoImportacao(SchemaBase):
    linha: int
    data: date
    descricao: str = Field(min_length=1, max_length=160)
    valor: Decimal = Field(gt=0, decimal_places=2)
    tipo: TipoMovimento
    natureza: Natureza
    categoria_id: int
    categoria_nome: str
    confianca: Decimal = Field(ge=0, le=1, decimal_places=2)
    justificativa: str = Field(max_length=240)
    fingerprint: str = Field(min_length=64, max_length=64)
    duplicada: bool = False


class ExtratoPreviewResponse(SchemaBase):
    arquivo_nome: str
    conta_existente_id: int | None
    conta_nome: str
    tipo_conta: TipoConta
    natureza_padrao: Natureza
    total_linhas: int
    total_creditos: Decimal
    total_debitos: Decimal
    classificado_por_ia: bool
    modelo: str | None = None
    aviso: str | None = None
    lancamentos: list[LancamentoImportacao]


class ExtratoConfirmRequest(SchemaBase):
    conta_id: int | None = None
    conta_nome: str = Field(min_length=1, max_length=80)
    tipo_conta: TipoConta = TipoConta.CORRENTE
    natureza: Natureza = Natureza.PESSOAL
    saldo_inicial: Decimal = Field(default=Decimal("0.00"), decimal_places=2)
    lancamentos: list[LancamentoImportacao] = Field(min_length=1, max_length=500)


class ExtratoConfirmResponse(SchemaBase):
    conta_id: int
    conta_nome: str
    importadas: int
    ignoradas_duplicadas: int
