"""Alinha o schema com docs/modelo-dados.md.

Cinco correcoes, todas com o "porque" em docs/modelo-dados.md:

1. FKs de usuario passam de CASCADE para RESTRICT (secao 3). O CASCADE nao
   funcionava: ao apagar um usuario o cascade bate no RESTRICT de transacao e a
   operacao inteira aborta - garantia de exclusao em cascata que so vale para
   usuario sem transacao nenhuma.
2. Unicidade de e-mail passa a ser sobre lower(email) (RN02). UNIQUE de coluna e
   case-sensitive e deixa Joao@x.com conviver com joao@x.com.
3. Unicidade de nome em conta e categoria passa a ser sobre lower(nome)
   (RN15 e secao 4).
4. meta ganha o UNIQUE (usuario_id, lower(nome)) que a secao 4 lista e que a
   0001 nao criou.
5. transacao ganha idx_transacao_data (secao 4) e o idx_transacao_conta_data e
   recriado com data DESC, que e a ordem em que o extrato e lido.

As FKs de transacao ja estavam corretas em ondelete; aqui elas so sao renomeadas
para o padrao fk_<tabela>_<coluna>, para que o nome no banco seja igual ao nome
no codigo e o downgrade seja previsivel.

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


def constraint_name(table: str, column: str, contype: str) -> str:
    """Descobre no catalogo o nome real da constraint.

    A 0001 criou as FKs e o UNIQUE de e-mail sem nome explicito, entao quem
    nomeou foi o Postgres. Consultar em vez de chutar deixa a migration correta
    mesmo que o banco tenha sido criado por outro caminho.
    """
    return op.get_bind().scalar(
        sa.text(
            """
            SELECT c.conname
            FROM pg_constraint c
            JOIN pg_attribute a
              ON a.attrelid = c.conrelid AND a.attnum = ANY (c.conkey)
            WHERE c.conrelid = :table::regclass
              AND c.contype = :contype
              AND a.attname = :column
            LIMIT 1
            """
        ),
        {"table": table, "column": column, "contype": contype},
    )


def upgrade() -> None:
    # 1. FKs de usuario: CASCADE -> RESTRICT. Mudar a acao exige recriar.
    for table in ("conta", "categoria", "meta"):
        op.drop_constraint(constraint_name(table, "usuario_id", "f"), table, type_="foreignkey")
        op.create_foreign_key(
            f"fk_{table}_usuario", table, "usuario", ["usuario_id"], ["id"], ondelete="RESTRICT"
        )

    # As FKs de transacao ja sao RESTRICT: so o nome muda.
    op.execute(
        f'ALTER TABLE transacao RENAME CONSTRAINT '
        f'"{constraint_name("transacao", "conta_id", "f")}" TO fk_transacao_conta'
    )
    op.execute(
        f'ALTER TABLE transacao RENAME CONSTRAINT '
        f'"{constraint_name("transacao", "categoria_id", "f")}" TO fk_transacao_categoria'
    )

    # 2. RN02: unicidade sobre lower(email).
    op.drop_constraint(constraint_name("usuario", "email", "u"), "usuario", type_="unique")
    op.create_index("uq_usuario_email", "usuario", [sa.text("lower(email)")], unique=True)

    # 3. lower(nome) em conta e categoria.
    op.drop_index("uq_conta_usuario_nome", table_name="conta")
    op.create_index(
        "uq_conta_usuario_nome", "conta", ["usuario_id", sa.text("lower(nome)")], unique=True
    )

    op.drop_index("uq_categoria_usuario", table_name="categoria")
    op.create_index(
        "uq_categoria_usuario",
        "categoria",
        ["usuario_id", sa.text("lower(nome)"), "tipo"],
        unique=True,
        postgresql_where=sa.text("usuario_id IS NOT NULL"),
    )
    op.drop_index("uq_categoria_sistema", table_name="categoria")
    op.create_index(
        "uq_categoria_sistema",
        "categoria",
        [sa.text("lower(nome)"), "tipo"],
        unique=True,
        postgresql_where=sa.text("usuario_id IS NULL"),
    )

    # 4. UNIQUE de nome em meta.
    op.create_index(
        "uq_meta_usuario_nome", "meta", ["usuario_id", sa.text("lower(nome)")], unique=True
    )

    # 5. Indices de transacao.
    op.drop_index("idx_transacao_conta_data", table_name="transacao")
    op.create_index(
        "idx_transacao_conta_data", "transacao", ["conta_id", sa.text("data DESC")]
    )
    op.create_index("idx_transacao_data", "transacao", ["data"])


def downgrade() -> None:
    op.drop_index("idx_transacao_data", table_name="transacao")
    op.drop_index("idx_transacao_conta_data", table_name="transacao")
    op.create_index("idx_transacao_conta_data", "transacao", ["conta_id", "data"])

    op.drop_index("uq_meta_usuario_nome", table_name="meta")

    op.drop_index("uq_categoria_sistema", table_name="categoria")
    op.create_index(
        "uq_categoria_sistema",
        "categoria",
        ["nome", "tipo"],
        unique=True,
        postgresql_where=sa.text("usuario_id IS NULL"),
    )
    op.drop_index("uq_categoria_usuario", table_name="categoria")
    op.create_index(
        "uq_categoria_usuario",
        "categoria",
        ["usuario_id", "nome", "tipo"],
        unique=True,
        postgresql_where=sa.text("usuario_id IS NOT NULL"),
    )

    op.drop_index("uq_conta_usuario_nome", table_name="conta")
    op.create_index("uq_conta_usuario_nome", "conta", ["usuario_id", "nome"], unique=True)

    op.drop_index("uq_usuario_email", table_name="usuario")
    op.create_unique_constraint("usuario_email_key", "usuario", ["email"])

    op.execute("ALTER TABLE transacao RENAME CONSTRAINT fk_transacao_categoria TO transacao_categoria_id_fkey")
    op.execute("ALTER TABLE transacao RENAME CONSTRAINT fk_transacao_conta TO transacao_conta_id_fkey")

    for table in ("meta", "categoria", "conta"):
        op.drop_constraint(f"fk_{table}_usuario", table, type_="foreignkey")
        op.create_foreign_key(
            f"{table}_usuario_id_fkey", table, "usuario", ["usuario_id"], ["id"], ondelete="CASCADE"
        )
