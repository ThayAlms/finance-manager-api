from datetime import date
from decimal import Decimal

from pydantic import ConfigDict, Field

from app.models.enums import Natureza
from app.schemas.common import SchemaBase


class ResumoNatureza(SchemaBase):
    """Os mesmos numeros do resumo, recortados em PESSOAL e NEGOCIO (RN14).

    Atencao ao criterio de cada campo, porque eles NAO usam a mesma coluna:

    - `saldo_contas` segue a natureza da **conta** — e de la que o dinheiro
      saiu ou entrou de fato;
    - `total_receitas` e `total_despesas` seguem a natureza da **transacao** —
      e a ela que o lancamento pertence.

    A diferenca e proposital. Pela RN14 o autonomo paga uma despesa do negocio
    pela conta pessoal: o saldo pessoal cai (o dinheiro saiu de la), mas a
    despesa e do negocio. Somar os dois pelo mesmo campo esconderia justamente
    o problema que o CaixaLivre existe para mostrar.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "natureza": "NEGOCIO",
                "saldo_contas": "2800.00",
                "total_receitas": "800.00",
                "total_despesas": "100.00",
                "economia": "700.00",
            }
        }
    )

    natureza: Natureza
    saldo_contas: Decimal = Field(
        description=(
            "Saldo acumulado das contas desta natureza. Não respeita o "
            "período: saldo é o histórico inteiro (RN07)."
        )
    )
    total_receitas: Decimal = Field(description="Receitas do período com esta natureza.")
    total_despesas: Decimal = Field(description="Despesas do período com esta natureza.")
    economia: Decimal = Field(
        description="`total_receitas − total_despesas`. Pode ser negativa."
    )


class ResumoResponse(SchemaBase):
    """Fotografia financeira de um mes.

    `saldo_total` e acumulado (todo o historico, RN07); receitas, despesas e
    economia sao do periodo delimitado por `inicio` e `fim`.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "mes": 9,
                "ano": 2026,
                "inicio": "2026-09-01",
                "fim": "2026-09-30",
                "saldo_total": "3550.00",
                "total_receitas": "800.00",
                "total_despesas": "250.00",
                "economia": "550.00",
                "quantidade_transacoes": 3,
                "por_natureza": [
                    {
                        "natureza": "PESSOAL",
                        "saldo_contas": "750.00",
                        "total_receitas": "0.00",
                        "total_despesas": "150.00",
                        "economia": "-150.00",
                    },
                    {
                        "natureza": "NEGOCIO",
                        "saldo_contas": "2800.00",
                        "total_receitas": "800.00",
                        "total_despesas": "100.00",
                        "economia": "700.00",
                    },
                ],
            }
        }
    )

    mes: int
    ano: int
    inicio: date = Field(description="Primeiro dia do mês consultado.")
    fim: date = Field(description="Último dia do mês consultado, calculado com `monthrange`.")
    saldo_total: Decimal = Field(
        description="Soma do saldo de todas as contas. Acumulado, não do período."
    )
    total_receitas: Decimal
    total_despesas: Decimal
    economia: Decimal = Field(
        description=(
            "`total_receitas − total_despesas` do período. Negativa quando "
            "gastou mais do que recebeu."
        )
    )
    quantidade_transacoes: int
    por_natureza: list[ResumoNatureza] = Field(
        description="Sempre traz PESSOAL e NEGOCIO, com zeros quando não houve movimento."
    )
