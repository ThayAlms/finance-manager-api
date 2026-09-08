from datetime import date

from fastapi import APIRouter, Query, Response, status

from app.core.database import DbSession
from app.core.security import CurrentUser
from app.models.enums import Natureza, TipoMovimento
from app.schemas import TransacaoCreate, TransacaoResponse
from app.services import transaction as service

router = APIRouter(prefix="/transacoes", tags=["Transações"])


@router.get(
    "",
    response_model=list[TransacaoResponse],
    summary="Listar transações por período, tipo e natureza",
    description=(
        "Devolve as transações das contas do usuário autenticado, da mais "
        "recente para a mais antiga.\n\n"
        "**Todos os filtros são opcionais e se acumulam.** Sem nenhum, a "
        "listagem devolve o histórico completo; combinados, respondem "
        "perguntas como *quanto o negócio gastou em agosto*: "
        "`?inicio=2026-08-01&fim=2026-08-31&tipo=DESPESA&natureza=NEGOCIO`. "
        "`inicio` posterior a `fim` responde `422`.\n\n"
        "O filtro de `natureza` usa a natureza **da transação**, não a da "
        "conta — é o mesmo critério do `GET /resumo`. Assim, filtrar por "
        "NEGOCIO aqui devolve exatamente o conjunto que soma o total do "
        "negócio no resumo, incluindo a despesa do negócio que foi paga pela "
        "conta pessoal (RN14). Filtrar pela conta faria os dois números "
        "divergirem.\n\n"
        "A transação não guarda `usuario_id` — o dono é alcançado por "
        "`transacao → conta → usuario`. Repetir o campo criaria dependência "
        "transitiva (3ª Forma Normal) e permitiria que a mesma transação "
        "tivesse dois donos diferentes conforme o caminho da consulta."
    ),
)
def list_all(
    usuario: CurrentUser,
    session: DbSession,
    inicio: date = Query(
        default=date(1900, 1, 1), description="Primeiro dia do período, inclusive."
    ),
    fim: date = Query(
        default=date(2999, 12, 31), description="Último dia do período, inclusive."
    ),
    tipo: TipoMovimento | None = Query(
        default=None, description="RECEITA ou DESPESA. Omitido, traz os dois."
    ),
    natureza: Natureza | None = Query(
        default=None,
        description="PESSOAL ou NEGOCIO, pela natureza da transação. Omitido, traz as duas.",
    ),
) -> list[TransacaoResponse]:
    return service.list_all(session, usuario, inicio, fim, tipo, natureza)


@router.get(
    "/{transacao_id}",
    response_model=TransacaoResponse,
    summary="Consultar transação",
    description=(
        "A resposta traz `conta_nome` e `categoria_nome` junto dos ids, para "
        "que o cliente monte o extrato sem uma segunda chamada por linha.\n\n"
        "Transação de outro usuário responde `404` (RN01)."
    ),
)
def find(
    transacao_id: int, usuario: CurrentUser, session: DbSession
) -> TransacaoResponse:
    return service.response(service.find(session, transacao_id, usuario))


@router.post(
    "",
    response_model=TransacaoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar transação",
    description=(
        "Concentra a maior parte das regras do sistema:\n\n"
        "- **valor sempre positivo** (RN04). O sinal do dinheiro vem do "
        "`tipo` — RECEITA soma, DESPESA subtrai —, nunca do valor. Guardar "
        "despesa como número negativo faz um erro de sinal virar saldo errado "
        "silencioso. Violação: `422`.\n"
        "- **tipo deve casar com o tipo da categoria** (RN05). É a validação "
        "mais fácil de esquecer, porque os dois campos são válidos "
        "isoladamente; é a combinação que não faz sentido. Sem ela dá para "
        "lançar Salário como despesa. Violação: `422`.\n"
        "- **conta e categoria precisam ser do usuário** (RN06). Sem essa "
        "checagem, bastaria passar o id na mão para lançar na conta de "
        "outro. Violação: `404`.\n"
        "- **data não pode ser futura** (RN13). Lançamento futuro é conta a "
        "pagar, outro conceito, fora do escopo — e faria o `/resumo` somar "
        "dinheiro que ainda não entrou. Violação: `422`.\n"
        "- **natureza é opcional e herda a da conta** quando omitida (RN14). "
        "Informe-a explicitamente no caso que o produto existe para resolver: "
        "a despesa do negócio paga pela conta pessoal."
    ),
)
def create(
    request: TransacaoCreate, usuario: CurrentUser, session: DbSession
) -> TransacaoResponse:
    return service.create(session, usuario, request)


@router.put(
    "/{transacao_id}",
    response_model=TransacaoResponse,
    summary="Atualizar transação",
    description=(
        "Substitui todos os campos e revalida as mesmas regras da criação, "
        "inclusive a troca de conta.\n\n"
        "Nenhum saldo precisa ser corrigido depois: como o saldo é calculado "
        "na leitura (RN07), mover a transação de conta já reflete nas duas."
    ),
)
def update(
    transacao_id: int,
    request: TransacaoCreate,
    usuario: CurrentUser,
    session: DbSession,
) -> TransacaoResponse:
    return service.update(session, usuario, transacao_id, request)


@router.delete(
    "/{transacao_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Excluir transação",
    description=(
        "Exclusão é definitiva — não há soft delete (R08). O saldo da conta "
        "volta ao valor correto sozinho, porque é recalculado do histórico a "
        "cada leitura (RN07)."
    ),
)
def delete(
    transacao_id: int, usuario: CurrentUser, session: DbSession
) -> Response:
    service.delete(session, usuario, transacao_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
