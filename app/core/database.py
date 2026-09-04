"""Conexao com o Postgres: engine, fabrica de sessoes e Base declarativa."""

from collections.abc import Generator
from typing import Annotated

from fastapi import Depends
from sqlalchemy import MetaData, create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings

# Nomes previsiveis para constraints e indices. Sem isso quem nomeia e o
# Postgres, com nomes que o Alembic nao consegue prever - e o downgrade de uma
# migration, que precisa do nome exato para dar DROP, deixa de ser confiavel.
# Atencao ao "ck": o template usa %(constraint_name)s, entao o nome passado em
# CheckConstraint(name=...) e o miolo, nao o nome final (valor_positivo em
# transacao vira ck_transacao_valor_positivo).
NAMING_CONVENTION = {
    "ix": "idx_%(table_name)s_%(column_0_N_name)s",
    "uq": "uq_%(table_name)s_%(column_0_N_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    """Classe base de todos os models. O Alembic le o schema por Base.metadata."""

    metadata = MetaData(naming_convention=NAMING_CONVENTION)


engine = create_engine(
    settings.database_url,
    # Descarta conexao morta antes de usar: o Postgres do Docker cai junto com o
    # container e o pool nao percebe sozinho.
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_db() -> Generator[Session, None, None]:
    """Abre uma sessao por requisicao e fecha no fim, mesmo se a rota falhar.

    Nao chame direto: quem chama e o FastAPI. Nas rotas use o alias DbSession.
    """
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


# Alias de dependencia usado nas rotas: `def listar(session: DbSession)`.
# Annotated carrega o tipo e o Depends juntos, entao o parametro fica
# obrigatorio e sem valor default (estilo recomendado pelo FastAPI).
DbSession = Annotated[Session, Depends(get_db)]
