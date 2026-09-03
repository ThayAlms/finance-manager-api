from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.models import Conta, Transacao


def all_by_user(
    session: Session, usuario_id: int, inicio: date, fim: date
) -> list[Transacao]:
    query = (
        select(Transacao)
        .join(Transacao.conta)
        .options(joinedload(Transacao.conta), joinedload(Transacao.categoria))
        .where(
            Conta.usuario_id == usuario_id,
            Transacao.data.between(inicio, fim),
        )
        .order_by(Transacao.data.desc(), Transacao.id.desc())
    )
    return list(session.scalars(query))


def by_id_for_user(session: Session, transacao_id: int, usuario_id: int) -> Transacao | None:
    return session.scalar(
        select(Transacao)
        .join(Transacao.conta)
        .options(joinedload(Transacao.conta), joinedload(Transacao.categoria))
        .where(Transacao.id == transacao_id, Conta.usuario_id == usuario_id)
    )


def count_by_account(session: Session, conta_id: int) -> int:
    return session.scalar(
        select(func.count()).select_from(Transacao).where(Transacao.conta_id == conta_id)
    ) or 0


def count_by_category(session: Session, categoria_id: int) -> int:
    return session.scalar(
        select(func.count()).select_from(Transacao).where(Transacao.categoria_id == categoria_id)
    ) or 0
