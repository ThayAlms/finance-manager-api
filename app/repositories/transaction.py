from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.models import Conta, Natureza, TipoMovimento, Transacao


def all_by_user(
    session: Session,
    usuario_id: int,
    inicio: date,
    fim: date,
    tipo: TipoMovimento | None = None,
    natureza: Natureza | None = None,
) -> list[Transacao]:
    """Transacoes das contas do usuario, da mais recente para a mais antiga.

    `tipo` e `natureza` sao opcionais e se acumulam com o periodo. O filtro de
    natureza usa `Transacao.natureza`, nao a da conta: e o mesmo criterio que
    o /resumo aplica em receitas e despesas, entao filtrar por NEGOCIO aqui
    devolve o conjunto que soma o total do negocio la. Filtrar pela conta
    faria os dois numeros divergirem (RN14).
    """
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
    if tipo is not None:
        query = query.where(Transacao.tipo == tipo)
    if natureza is not None:
        query = query.where(Transacao.natureza == natureza)
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
