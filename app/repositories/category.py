from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models import Categoria, TipoMovimento


def visible_to(session: Session, usuario_id: int) -> list[Categoria]:
    query = (
        select(Categoria)
        .where(or_(Categoria.usuario_id == usuario_id, Categoria.usuario_id.is_(None)))
        .order_by(Categoria.nome)
    )
    return list(session.scalars(query))


def by_id_visible(session: Session, categoria_id: int, usuario_id: int) -> Categoria | None:
    return session.scalar(
        select(Categoria).where(
            Categoria.id == categoria_id,
            or_(Categoria.usuario_id == usuario_id, Categoria.usuario_id.is_(None)),
        )
    )


def duplicate(
    session: Session,
    usuario_id: int,
    nome: str,
    tipo: TipoMovimento,
    exclude_id: int | None = None,
) -> Categoria | None:
    query = select(Categoria).where(
        Categoria.usuario_id == usuario_id,
        Categoria.tipo == tipo,
        func.lower(Categoria.nome) == nome.lower(),
    )
    if exclude_id is not None:
        query = query.where(Categoria.id != exclude_id)
    return session.scalar(query)
