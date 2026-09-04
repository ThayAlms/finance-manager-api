"""Cria o schema inicial do CaixaLivre.

Revision ID: 0001
Revises:
"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    bind = op.get_bind()
    tipo_movimento = postgresql.ENUM("RECEITA", "DESPESA", name="tipo_movimento")
    tipo_conta = postgresql.ENUM("CORRENTE", "POUPANCA", "CARTEIRA", name="tipo_conta")
    natureza = postgresql.ENUM("PESSOAL", "NEGOCIO", name="natureza")
    tipo_movimento.create(bind, checkfirst=True)
    tipo_conta.create(bind, checkfirst=True)
    natureza.create(bind, checkfirst=True)

    def timestamps():
        return (
            sa.Column("criado_em", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("atualizado_em", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        )

    op.create_table(
        "usuario",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("nome", sa.String(120), nullable=False),
        sa.Column("email", sa.String(180), nullable=False, unique=True),
        sa.Column("senha_hash", sa.String(255), nullable=False),
        *timestamps(),
    )
    op.create_table(
        "conta",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("usuario_id", sa.BigInteger(), sa.ForeignKey("usuario.id", ondelete="CASCADE"), nullable=False),
        sa.Column("nome", sa.String(80), nullable=False),
        sa.Column("tipo", postgresql.ENUM(name="tipo_conta", create_type=False), nullable=False),
        sa.Column("natureza", postgresql.ENUM(name="natureza", create_type=False), nullable=False),
        sa.Column("saldo_inicial", sa.Numeric(14, 2), server_default="0", nullable=False),
        *timestamps(),
    )
    op.create_index("uq_conta_usuario_nome", "conta", ["usuario_id", "nome"], unique=True)
    op.create_index("idx_conta_usuario", "conta", ["usuario_id"])

    op.create_table(
        "categoria",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("usuario_id", sa.BigInteger(), sa.ForeignKey("usuario.id", ondelete="CASCADE"), nullable=True),
        sa.Column("nome", sa.String(60), nullable=False),
        sa.Column("tipo", postgresql.ENUM(name="tipo_movimento", create_type=False), nullable=False),
        *timestamps(),
    )
    op.create_index("idx_categoria_usuario", "categoria", ["usuario_id"])
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

    op.create_table(
        "transacao",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("conta_id", sa.BigInteger(), sa.ForeignKey("conta.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("categoria_id", sa.BigInteger(), sa.ForeignKey("categoria.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("descricao", sa.String(160), nullable=False),
        sa.Column("valor", sa.Numeric(14, 2), nullable=False),
        sa.Column("data", sa.Date(), nullable=False),
        sa.Column("tipo", postgresql.ENUM(name="tipo_movimento", create_type=False), nullable=False),
        sa.Column("natureza", postgresql.ENUM(name="natureza", create_type=False), nullable=False),
        *timestamps(),
        sa.CheckConstraint("valor > 0", name="ck_transacao_valor_positivo"),
    )
    op.create_index("idx_transacao_conta_data", "transacao", ["conta_id", "data"])
    op.create_index("idx_transacao_categoria", "transacao", ["categoria_id"])

    op.create_table(
        "meta",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("usuario_id", sa.BigInteger(), sa.ForeignKey("usuario.id", ondelete="CASCADE"), nullable=False),
        sa.Column("nome", sa.String(80), nullable=False),
        sa.Column("valor_meta", sa.Numeric(14, 2), nullable=False),
        sa.Column("valor_atual", sa.Numeric(14, 2), server_default="0", nullable=False),
        sa.Column("prazo", sa.Date(), nullable=True),
        *timestamps(),
        sa.CheckConstraint("valor_meta > 0", name="ck_meta_valor_positivo"),
        sa.CheckConstraint("valor_atual >= 0", name="ck_meta_atual_nao_negativo"),
    )
    op.create_index("idx_meta_usuario", "meta", ["usuario_id"])

    categoria = sa.table(
        "categoria",
        sa.column("usuario_id", sa.BigInteger()),
        sa.column("nome", sa.String()),
        sa.column("tipo", postgresql.ENUM(name="tipo_movimento", create_type=False)),
    )
    op.bulk_insert(
        categoria,
        [
            {"usuario_id": None, "nome": nome, "tipo": tipo}
            for tipo, nomes in {
                "RECEITA": ["Salário", "Vendas", "Serviços prestados", "Investimentos", "Outras receitas"],
                "DESPESA": ["Alimentação", "Transporte", "Moradia", "Saúde", "Educação", "Lazer", "Assinaturas", "Impostos e taxas", "Ferramentas e software", "Outras despesas"],
            }.items()
            for nome in nomes
        ],
    )


def downgrade() -> None:
    bind = op.get_bind()
    op.drop_table("meta")
    op.drop_table("transacao")
    op.drop_table("categoria")
    op.drop_table("conta")
    op.drop_table("usuario")
    postgresql.ENUM(name="natureza").drop(bind, checkfirst=True)
    postgresql.ENUM(name="tipo_conta").drop(bind, checkfirst=True)
    postgresql.ENUM(name="tipo_movimento").drop(bind, checkfirst=True)
