"""Normaliza unicidade case-insensitive para a CP2.

Revision ID: 0002
Revises: 0001
"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0002"
down_revision: str | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.drop_constraint("usuario_email_key", "usuario", type_="unique")
    op.drop_index("uq_conta_usuario_nome", table_name="conta")
    op.drop_index("uq_categoria_usuario", table_name="categoria")
    op.drop_index("uq_categoria_sistema", table_name="categoria")

    op.create_index(
        "uq_usuario_email_lower",
        "usuario",
        [sa.text("lower(email)")],
        unique=True,
    )
    op.create_index(
        "uq_conta_usuario_nome",
        "conta",
        ["usuario_id", sa.text("lower(nome)")],
        unique=True,
    )
    op.create_index(
        "uq_categoria_usuario",
        "categoria",
        ["usuario_id", sa.text("lower(nome)"), "tipo"],
        unique=True,
        postgresql_where=sa.text("usuario_id IS NOT NULL"),
    )
    op.create_index(
        "uq_categoria_sistema",
        "categoria",
        [sa.text("lower(nome)"), "tipo"],
        unique=True,
        postgresql_where=sa.text("usuario_id IS NULL"),
    )
    op.create_index(
        "uq_meta_usuario_nome",
        "meta",
        ["usuario_id", sa.text("lower(nome)")],
        unique=True,
    )
    op.create_index(
        "idx_transacao_natureza_data",
        "transacao",
        ["natureza", "data"],
    )
    op.create_index(
        "idx_transacao_tipo_data",
        "transacao",
        ["tipo", "data"],
    )


def downgrade() -> None:
    op.drop_index("idx_transacao_tipo_data", table_name="transacao")
    op.drop_index("idx_transacao_natureza_data", table_name="transacao")
    op.drop_index("uq_meta_usuario_nome", table_name="meta")
    op.drop_index("uq_categoria_sistema", table_name="categoria")
    op.drop_index("uq_categoria_usuario", table_name="categoria")
    op.drop_index("uq_conta_usuario_nome", table_name="conta")
    op.drop_index("uq_usuario_email_lower", table_name="usuario")

    op.create_unique_constraint("usuario_email_key", "usuario", ["email"])
    op.create_index(
        "uq_conta_usuario_nome", "conta", ["usuario_id", "nome"], unique=True
    )
    op.create_index(
        "uq_categoria_usuario",
        "categoria",
        ["usuario_id", "nome", "tipo"],
        unique=True,
        postgresql_where=sa.text("usuario_id IS NOT NULL"),
    )
    op.create_index(
        "uq_categoria_sistema",
        "categoria",
        ["nome", "tipo"],
        unique=True,
        postgresql_where=sa.text("usuario_id IS NULL"),
    )
