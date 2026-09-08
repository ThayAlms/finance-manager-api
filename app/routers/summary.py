from fastapi import APIRouter, Query

from app.core.database import DbSession
from app.core.security import CurrentUser
from app.schemas import ResumoResponse
from app.services import summary as service

router = APIRouter(prefix="/resumo", tags=["Resumo"])


@router.get(
    "",
    response_model=ResumoResponse,
    summary="Consultar resumo financeiro do mês",
    description=(
        "Devolve saldo, receitas, despesas e economia do mês, com a quebra em "
        "PESSOAL e NEGOCIO que é o recorte do CaixaLivre (RN14).\n\n"
        "Sem parâmetros, responde pelo mês corrente. Os limites de `ano` "
        "acompanham o intervalo aceito em `GET /transacoes`.\n\n"
        "**Saldo e economia usam critérios diferentes de propósito:** o saldo "
        "segue a natureza da conta (de onde o dinheiro saiu) e receitas e "
        "despesas seguem a natureza da transação (a quem o lançamento "
        "pertence). Pela RN14 uma despesa do negócio pode ser paga pela conta "
        "pessoal, e é essa divergência que o resumo precisa mostrar."
    ),
)
def find(
    usuario: CurrentUser,
    session: DbSession,
    mes: int | None = Query(default=None, ge=1, le=12, description="Mês. Padrão: mês atual."),
    ano: int | None = Query(
        default=None, ge=1900, le=2999, description="Ano. Padrão: ano atual."
    ),
) -> ResumoResponse:
    return service.month_summary(session, usuario, mes, ano)
