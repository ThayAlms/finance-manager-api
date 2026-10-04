from datetime import date
from decimal import Decimal

from sqlalchemy import case, extract, func, select
from sqlalchemy.orm import Session

from app.models import Categoria, Conta, Natureza, TipoMovimento, Transacao


def _money(value) -> Decimal:
    return Decimal(value or 0).quantize(Decimal("0.01"))


def totals(session: Session, usuario_id: int, inicio: date, fim: date) -> tuple[Decimal, Decimal]:
    row = session.execute(
        select(
            func.coalesce(
                func.sum(
                    case(
                        (Transacao.tipo == TipoMovimento.RECEITA, Transacao.valor),
                        else_=0,
                    )
                ),
                0,
            ),
            func.coalesce(
                func.sum(
                    case(
                        (Transacao.tipo == TipoMovimento.DESPESA, Transacao.valor),
                        else_=0,
                    )
                ),
                0,
            ),
        )
        .select_from(Transacao)
        .join(Transacao.conta)
        .where(Conta.usuario_id == usuario_id, Transacao.data.between(inicio, fim))
    ).one()
    return _money(row[0]), _money(row[1])


def total_balance(session: Session, usuario_id: int) -> Decimal:
    movement = case(
        (Transacao.tipo == TipoMovimento.RECEITA, Transacao.valor),
        else_=-Transacao.valor,
    )
    transaction_total = session.scalar(
        select(func.coalesce(func.sum(movement), 0))
        .select_from(Transacao)
        .join(Transacao.conta)
        .where(Conta.usuario_id == usuario_id)
    )
    initial_total = session.scalar(
        select(func.coalesce(func.sum(Conta.saldo_inicial), 0)).where(
            Conta.usuario_id == usuario_id
        )
    )
    return _money(Decimal(initial_total or 0) + Decimal(transaction_total or 0))


def by_nature(session: Session, usuario_id: int, inicio: date, fim: date) -> list[dict]:
    rows = session.execute(
        select(
            Transacao.natureza,
            func.sum(
                case(
                    (Transacao.tipo == TipoMovimento.RECEITA, Transacao.valor),
                    else_=0,
                )
            ),
            func.sum(
                case(
                    (Transacao.tipo == TipoMovimento.DESPESA, Transacao.valor),
                    else_=0,
                )
            ),
        )
        .join(Transacao.conta)
        .where(Conta.usuario_id == usuario_id, Transacao.data.between(inicio, fim))
        .group_by(Transacao.natureza)
    ).all()
    indexed = {natureza: (_money(receitas), _money(despesas)) for natureza, receitas, despesas in rows}
    return [
        {
            "natureza": natureza,
            "receitas": indexed.get(natureza, (Decimal("0.00"), Decimal("0.00")))[0],
            "despesas": indexed.get(natureza, (Decimal("0.00"), Decimal("0.00")))[1],
            "resultado": indexed.get(natureza, (Decimal("0.00"), Decimal("0.00")))[0]
            - indexed.get(natureza, (Decimal("0.00"), Decimal("0.00")))[1],
        }
        for natureza in Natureza
    ]


def by_category(session: Session, usuario_id: int, inicio: date, fim: date) -> list[dict]:
    rows = session.execute(
        select(
            Categoria.id,
            Categoria.nome,
            Transacao.tipo,
            func.sum(Transacao.valor).label("total"),
        )
        .select_from(Transacao)
        .join(Transacao.conta)
        .join(Transacao.categoria)
        .where(Conta.usuario_id == usuario_id, Transacao.data.between(inicio, fim))
        .group_by(Categoria.id, Categoria.nome, Transacao.tipo)
        .order_by(func.sum(Transacao.valor).desc())
    ).all()
    return [
        {
            "categoria_id": category_id,
            "categoria_nome": name,
            "tipo": movement_type,
            "total": _money(total),
        }
        for category_id, name, movement_type, total in rows
    ]


def monthly(session: Session, usuario_id: int, inicio: date, fim: date) -> list[dict]:
    year = extract("year", Transacao.data)
    month = extract("month", Transacao.data)
    rows = session.execute(
        select(
            year.label("ano"),
            month.label("mes"),
            func.sum(
                case(
                    (Transacao.tipo == TipoMovimento.RECEITA, Transacao.valor),
                    else_=0,
                )
            ),
            func.sum(
                case(
                    (Transacao.tipo == TipoMovimento.DESPESA, Transacao.valor),
                    else_=0,
                )
            ),
        )
        .select_from(Transacao)
        .join(Transacao.conta)
        .where(Conta.usuario_id == usuario_id, Transacao.data.between(inicio, fim))
        .group_by(year, month)
        .order_by(year, month)
    ).all()
    result = []
    for year_value, month_value, receitas, despesas in rows:
        income = _money(receitas)
        expense = _money(despesas)
        result.append(
            {
                "mes": f"{int(year_value):04d}-{int(month_value):02d}",
                "receitas": income,
                "despesas": expense,
                "resultado": income - expense,
            }
        )
    return result
