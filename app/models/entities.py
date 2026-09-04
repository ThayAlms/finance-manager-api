from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import BigInteger, CheckConstraint, Date, DateTime, Enum, ForeignKey, Index, Integer, Numeric, String, func, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import Natureza, TipoConta, TipoMovimento

ID_TYPE = BigInteger().with_variant(Integer, "sqlite")


class TimestampMixin:
    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


class Usuario(TimestampMixin, Base):
    __tablename__ = "usuario"

    id: Mapped[int] = mapped_column(ID_TYPE, primary_key=True)
    nome: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(180), nullable=False, unique=True)
    senha_hash: Mapped[str] = mapped_column(String(255), nullable=False)


class Conta(TimestampMixin, Base):
    __tablename__ = "conta"
    __table_args__ = (
        Index("uq_conta_usuario_nome", "usuario_id", "nome", unique=True),
        Index("idx_conta_usuario", "usuario_id"),
    )

    id: Mapped[int] = mapped_column(ID_TYPE, primary_key=True)
    usuario_id: Mapped[int] = mapped_column(
        ID_TYPE,
        ForeignKey("usuario.id", ondelete="CASCADE"), nullable=False
    )
    nome: Mapped[str] = mapped_column(String(80), nullable=False)
    tipo: Mapped[TipoConta] = mapped_column(Enum(TipoConta, name="tipo_conta"), nullable=False)
    natureza: Mapped[Natureza] = mapped_column(Enum(Natureza, name="natureza"), nullable=False)
    saldo_inicial: Mapped[Decimal] = mapped_column(
        Numeric(14, 2), nullable=False, default=Decimal("0.00")
    )
    usuario: Mapped[Usuario] = relationship()


class Categoria(TimestampMixin, Base):
    __tablename__ = "categoria"
    __table_args__ = (
        Index(
            "uq_categoria_usuario",
            "usuario_id",
            "nome",
            "tipo",
            unique=True,
            postgresql_where=text("usuario_id IS NOT NULL"),
        ),
        Index(
            "uq_categoria_sistema",
            "nome",
            "tipo",
            unique=True,
            postgresql_where=text("usuario_id IS NULL"),
        ),
        Index("idx_categoria_usuario", "usuario_id"),
    )

    id: Mapped[int] = mapped_column(ID_TYPE, primary_key=True)
    usuario_id: Mapped[int | None] = mapped_column(
        ID_TYPE,
        ForeignKey("usuario.id", ondelete="CASCADE"), nullable=True
    )
    nome: Mapped[str] = mapped_column(String(60), nullable=False)
    tipo: Mapped[TipoMovimento] = mapped_column(
        Enum(TipoMovimento, name="tipo_movimento"), nullable=False
    )
    usuario: Mapped[Usuario | None] = relationship()


class Transacao(TimestampMixin, Base):
    __tablename__ = "transacao"
    __table_args__ = (
        CheckConstraint("valor > 0", name="ck_transacao_valor_positivo"),
        Index("idx_transacao_conta_data", "conta_id", "data"),
        Index("idx_transacao_categoria", "categoria_id"),
    )

    id: Mapped[int] = mapped_column(ID_TYPE, primary_key=True)
    conta_id: Mapped[int] = mapped_column(
        ID_TYPE,
        ForeignKey("conta.id", ondelete="RESTRICT"), nullable=False
    )
    categoria_id: Mapped[int] = mapped_column(
        ID_TYPE,
        ForeignKey("categoria.id", ondelete="RESTRICT"), nullable=False
    )
    descricao: Mapped[str] = mapped_column(String(160), nullable=False)
    valor: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    data: Mapped[date] = mapped_column(Date, nullable=False)
    tipo: Mapped[TipoMovimento] = mapped_column(
        Enum(TipoMovimento, name="tipo_movimento"), nullable=False
    )
    natureza: Mapped[Natureza] = mapped_column(
        Enum(Natureza, name="natureza"), nullable=False
    )
    conta: Mapped[Conta] = relationship()
    categoria: Mapped[Categoria] = relationship()


class Meta(TimestampMixin, Base):
    __tablename__ = "meta"
    __table_args__ = (
        CheckConstraint("valor_meta > 0", name="ck_meta_valor_positivo"),
        CheckConstraint("valor_atual >= 0", name="ck_meta_atual_nao_negativo"),
        Index("idx_meta_usuario", "usuario_id"),
    )

    id: Mapped[int] = mapped_column(ID_TYPE, primary_key=True)
    usuario_id: Mapped[int] = mapped_column(
        ID_TYPE,
        ForeignKey("usuario.id", ondelete="CASCADE"), nullable=False
    )
    nome: Mapped[str] = mapped_column(String(80), nullable=False)
    valor_meta: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    valor_atual: Mapped[Decimal] = mapped_column(
        Numeric(14, 2), nullable=False, default=Decimal("0.00")
    )
    prazo: Mapped[date | None] = mapped_column(Date, nullable=True)
    usuario: Mapped[Usuario] = relationship()
