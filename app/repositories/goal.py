from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Meta


def all_by_user(session: Session, usuario_id: int) -> list[Meta]:
    return list(
        session.scalars(
            select(Meta)
            .where(Meta.usuario_id == usuario_id)
            .order_by(Meta.prazo.asc(), Meta.nome)
        )
    )


def by_id_for_user(session: Session, meta_id: int, usuario_id: int) -> Meta | None:
    return session.scalar(
        select(Meta).where(Meta.id == meta_id, Meta.usuario_id == usuario_id)
    )
