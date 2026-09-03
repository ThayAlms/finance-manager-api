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


def by_id_for_user(session: Session, conta_id: int, usuario_id: int) -> Conta | None:
    return session.scalar(
        select(Conta).where(Conta.id == conta_id, Conta.usuario_id == usuario_id)
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
