from datetime import date
from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy.orm import Session

from app.core.errors import unprocessable
from app.models import Usuario
from app.repositories import dashboard as repository
from app.schemas.dashboard import ResumoResponse


def summary(session: Session, usuario: Usuario, inicio: date, fim: date) -> ResumoResponse:
    if inicio > fim:
        unprocessable("A data inicial não pode ser posterior à data final")
    receitas, despesas = repository.totals(session, usuario.id, inicio, fim)
    savings_rate = (
        ((receitas - despesas) / receitas * Decimal("100"))
        .quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        if receitas > 0
        else Decimal("0.00")
    )
    return ResumoResponse(
        inicio=inicio,
        fim=fim,
        saldo_total=repository.total_balance(session, usuario.id),
        receitas=receitas,
        despesas=despesas,
        resultado=receitas - despesas,
        taxa_economia=savings_rate,
        por_natureza=repository.by_nature(session, usuario.id, inicio, fim),
        por_categoria=repository.by_category(session, usuario.id, inicio, fim),
        evolucao_mensal=repository.monthly(session, usuario.id, inicio, fim),
    )
