from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Usuario


def by_id(session: Session, usuario_id: int) -> Usuario | None:
    return session.get(Usuario, usuario_id)


def by_email(session: Session, email: str) -> Usuario | None:
    return session.scalar(select(Usuario).where(Usuario.email == email))


def save(session: Session, usuario: Usuario) -> Usuario:
    session.add(usuario)
    session.commit()
    session.refresh(usuario)
    return usuario
