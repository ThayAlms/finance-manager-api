"""Agregacoes do resumo financeiro.

Sao tres consultas e nao uma so de proposito. Saldo e agrupado pela natureza
da CONTA (onde o dinheiro esta) e receita/despesa pela natureza da TRANSACAO
(a que o lancamento pertence) — criterios diferentes, que a RN14 permite
divergir. Unir os dois num unico SELECT exigiria FULL OUTER JOIN entre eixos
distintos, ilegivel e sem ganho nenhum neste volume.
"""

from datetime import date
from decimal import Decimal

from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from app.models import Conta, Natureza, TipoMovimento, Transacao

ZERO = Decimal("0.00")


def to_decimal(value) -> Decimal:
    """Converte o retorno do driver em Decimal sem passar por float.

    No Postgres, NUMERIC ja volta como Decimal. No SQLite dos testes a soma
    volta como float, e `Decimal(1200.55)` guarda o lixo binario do float —
    exatamente o que a RN17 proibe. Passar por str corta esse caminho.
    """
    if value is None:
        return ZERO
    if isinstance(value, Decimal):
        return value
    return Decimal(str(value))


def _movement() -> case:
    """RECEITA soma, DESPESA subtrai. O sinal vem do tipo, nunca do valor (RN04)."""
    return case(
        (Transacao.tipo == TipoMovimento.RECEITA, Transacao.valor),
        else_=-Transacao.valor,
    )


def balance_by_nature(session: Session, usuario_id: int) -> dict[Natureza, Decimal]:
    """Saldo acumulado por natureza da conta: saldo_inicial + movimento (RN07).

    Sem recorte de periodo: saldo e o historico inteiro. Filtrar por mes daria
    "quanto entrou no mes", que e a economia — outro numero.
    """
    saldos = {natureza: ZERO for natureza in Natureza}

    iniciais = session.execute(
        select(Conta.natureza, func.coalesce(func.sum(Conta.saldo_inicial), 0))
        .where(Conta.usuario_id == usuario_id)
        .group_by(Conta.natureza)
    )
    for natureza, total in iniciais:
        saldos[natureza] = saldos[natureza] + to_decimal(total)

    movimentos = session.execute(
        select(Conta.natureza, func.coalesce(func.sum(_movement()), 0))
        .select_from(Transacao)
        .join(Transacao.conta)
        .where(Conta.usuario_id == usuario_id)
        .group_by(Conta.natureza)
    )
    for natureza, total in movimentos:
        saldos[natureza] = saldos[natureza] + to_decimal(total)

    return saldos


def totals_by_nature(
    session: Session, usuario_id: int, inicio: date, fim: date
) -> dict[Natureza, tuple[Decimal, Decimal]]:
    """Receitas e despesas do periodo, por natureza da transacao.

    Devolve {natureza: (receitas, despesas)}, sempre com as duas naturezas
    presentes — mes sem lancamento nenhum vira zero, nao vira chave ausente.
    """
    receita = case((Transacao.tipo == TipoMovimento.RECEITA, Transacao.valor), else_=0)
    despesa = case((Transacao.tipo == TipoMovimento.DESPESA, Transacao.valor), else_=0)

    totais = {natureza: (ZERO, ZERO) for natureza in Natureza}
    linhas = session.execute(
        select(
            Transacao.natureza,
            func.coalesce(func.sum(receita), 0),
            func.coalesce(func.sum(despesa), 0),
        )
        .select_from(Transacao)
        .join(Transacao.conta)
        .where(Conta.usuario_id == usuario_id, Transacao.data.between(inicio, fim))
        .group_by(Transacao.natureza)
    )
    for natureza, receitas, despesas in linhas:
        totais[natureza] = (to_decimal(receitas), to_decimal(despesas))
    return totais


def count_in_period(session: Session, usuario_id: int, inicio: date, fim: date) -> int:
    return session.scalar(
        select(func.count())
        .select_from(Transacao)
        .join(Transacao.conta)
        .where(Conta.usuario_id == usuario_id, Transacao.data.between(inicio, fim))
    ) or 0
