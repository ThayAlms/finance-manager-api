"""Resumo financeiro do mes.

Nao ha escrita aqui: o resumo e leitura pura, montada a partir das agregacoes
do repository. Nenhum numero e persistido — mesmo principio da RN07 e da RN11,
campo derivado se calcula na leitura para nao ter como divergir da origem.
"""

from calendar import monthrange
from datetime import date
from decimal import Decimal

from sqlalchemy.orm import Session

from app.models import Natureza, Usuario
from app.repositories import summary as repository
from app.schemas import ResumoNatureza, ResumoResponse

CENTAVOS = Decimal("0.01")


def _round(value: Decimal) -> Decimal:
    """Fixa duas casas na saida. NUMERIC(14,2) ja garante isso no banco, mas a
    soma do SQLite nos testes pode voltar com mais casas."""
    return value.quantize(CENTAVOS)


def period(mes: int | None, ano: int | None) -> tuple[int, int, date, date]:
    """Resolve mes/ano no primeiro e ultimo dia. Sem parametro, e o mes atual.

    O ultimo dia sai de `monthrange` em vez de uma tabela de 30/31: fevereiro
    de ano bissexto e o caso que uma tabela escrita na mao erra.
    """
    hoje = date.today()
    mes = mes or hoje.month
    ano = ano or hoje.year
    ultimo_dia = monthrange(ano, mes)[1]
    return mes, ano, date(ano, mes, 1), date(ano, mes, ultimo_dia)


def month_summary(
    session: Session, usuario: Usuario, mes: int | None = None, ano: int | None = None
) -> ResumoResponse:
    mes, ano, inicio, fim = period(mes, ano)

    saldos = repository.balance_by_nature(session, usuario.id)
    totais = repository.totals_by_nature(session, usuario.id, inicio, fim)

    por_natureza = []
    for natureza in Natureza:
        receitas, despesas = totais[natureza]
        por_natureza.append(
            ResumoNatureza(
                natureza=natureza,
                saldo_contas=_round(saldos[natureza]),
                total_receitas=_round(receitas),
                total_despesas=_round(despesas),
                economia=_round(receitas - despesas),
            )
        )

    receitas = sum((linha.total_receitas for linha in por_natureza), Decimal("0.00"))
    despesas = sum((linha.total_despesas for linha in por_natureza), Decimal("0.00"))

    return ResumoResponse(
        mes=mes,
        ano=ano,
        inicio=inicio,
        fim=fim,
        saldo_total=_round(sum((linha.saldo_contas for linha in por_natureza), Decimal("0.00"))),
        total_receitas=_round(receitas),
        total_despesas=_round(despesas),
        economia=_round(receitas - despesas),
        quantidade_transacoes=repository.count_in_period(session, usuario.id, inicio, fim),
        por_natureza=por_natureza,
    )
