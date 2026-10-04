"""Adiciona controle de duplicidade para importação de extratos.

Revision ID: 0003
Revises: 0002
"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0003"
down_revision: str | None = "0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("transacao", sa.Column("import_hash", sa.String(64), nullable=True))
    op.create_index(
        "uq_transacao_conta_import_hash",
        "transacao",
        ["conta_id", "import_hash"],
        unique=True,
        postgresql_where=sa.text("import_hash IS NOT NULL"),
    )


def downgrade() -> None:
    op.drop_index("uq_transacao_conta_import_hash", table_name="transacao")
    op.drop_column("transacao", "import_hash")
