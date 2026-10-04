from decimal import Decimal

from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from app.models import Conta, TipoMovimento, Transacao


def all_by_user(session: Session, usuario_id: int) -> list[Conta]:
    return list(
        session.scalars(
            select(Conta).where(Conta.usuario_id == usuario_id).order_by(Conta.nome)
        )
    )


def all_with_balance_by_user(
    session: Session, usuario_id: int
) -> list[tuple[Conta, Decimal]]:
    movement = case(
        (Transacao.tipo == TipoMovimento.RECEITA, Transacao.valor),
        else_=-Transacao.valor,
    )
    totals = (
        select(
            Transacao.conta_id.label("conta_id"),
            func.sum(movement).label("movimentacao"),
        )
        .group_by(Transacao.conta_id)
        .subquery()
    )
    query = (
        select(
            Conta,
            (Conta.saldo_inicial + func.coalesce(totals.c.movimentacao, 0)).label(
                "saldo_atual"
            ),
        )
        .outerjoin(totals, totals.c.conta_id == Conta.id)
        .where(Conta.usuario_id == usuario_id)
        .order_by(Conta.nome)
    )
    return [(conta, Decimal(saldo)) for conta, saldo in session.execute(query).all()]


def by_id_for_user(session: Session, conta_id: int, usuario_id: int) -> Conta | None:
    return session.scalar(
        select(Conta).where(Conta.id == conta_id, Conta.usuario_id == usuario_id)
    )


def by_name_for_user(session: Session, nome: str, usuario_id: int) -> Conta | None:
    return session.scalar(
        select(Conta).where(
            Conta.usuario_id == usuario_id,
            Conta.nome.ilike(nome.strip()),
        )
    )


def duplicate(
    session: Session, usuario_id: int, nome: str, exclude_id: int | None = None
) -> Conta | None:
    query = select(Conta).where(Conta.usuario_id == usuario_id, Conta.nome.ilike(nome))
    if exclude_id is not None:
        query = query.where(Conta.id != exclude_id)
    return session.scalar(query)


def current_balance(session: Session, conta: Conta) -> Decimal:
    movement = case(
        (Transacao.tipo == TipoMovimento.RECEITA, Transacao.valor),
        else_=-Transacao.valor,
    )
    total = session.scalar(
        select(func.coalesce(func.sum(movement), 0)).where(Transacao.conta_id == conta.id)
    )
    return Decimal(conta.saldo_inicial) + Decimal(total or 0)
