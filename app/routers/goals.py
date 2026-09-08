from fastapi import APIRouter, Response, status

from app.core.database import DbSession
from app.core.security import CurrentUser
from app.schemas import MetaCreate, MetaResponse
from app.services import goal as service

router = APIRouter(prefix="/metas", tags=["Metas"])


@router.get(
    "",
    response_model=list[MetaResponse],
    summary="Listar metas e progresso",
    description=(
        "Metas do usuário autenticado, ordenadas por prazo.\n\n"
        "`valor_restante`, `progresso_percentual` e `atingida` são calculados "
        "na leitura, nunca armazenados (RN11 e RN12) — coluna derivada "
        "precisaria ser reescrita a cada aporte, e um caminho esquecido "
        "deixaria a barra de progresso mentindo."
    ),
)
def list_all(usuario: CurrentUser, session: DbSession) -> list[MetaResponse]:
    return service.list_all(session, usuario)


@router.get(
    "/{meta_id}",
    response_model=MetaResponse,
    summary="Consultar meta",
    description=(
        "`progresso_percentual` é limitado a 100 e `valor_restante` a 0 "
        "(RN11). A meta pode ser ultrapassada, já que o `valor_atual` é "
        "digitado à mão (R07); sem os limites a API devolveria 137% concluído "
        "e faltam −350,00, e cada cliente teria que tratar isso por conta.\n\n"
        "`atingida` usa `valor_atual >= valor_meta` e é decidido aqui, num "
        "lugar só: se cada tela refizesse a comparação, uma delas usaria `>` "
        "e a meta batida na régua apareceria concluída numa e pendente noutra."
    ),
)
def find(meta_id: int, usuario: CurrentUser, session: DbSession) -> MetaResponse:
    return service.response(service.find(session, meta_id, usuario))


@router.post(
    "",
    response_model=MetaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar meta",
    description=(
        "`valor_meta` deve ser maior que zero (RN11): meta zerada faria o "
        "cálculo de progresso dividir por zero e derrubar o endpoint com "
        "`500`, e meta negativa não quer dizer nada. Violação: `422`.\n\n"
        "`valor_atual` é opcional e começa em 0. Ele é alimentado à mão (R07) "
        "— derivar dos lançamentos exigiria definir quais transações contam "
        "como aporte, o que ficou para a próxima versão.\n\n"
        "Nome repetido no mesmo usuário responde `409`: duas metas de mesmo "
        "nome são clique duplo ou erro de digitação, e deixam o usuário com "
        "duas barras de progresso pela metade."
    ),
)
def create(
    request: MetaCreate, usuario: CurrentUser, session: DbSession
) -> MetaResponse:
    return service.create(session, usuario, request)


@router.put(
    "/{meta_id}",
    response_model=MetaResponse,
    summary="Atualizar meta",
    description=(
        "Substitui todos os campos. É por aqui que o usuário registra um "
        "aporte, alterando o `valor_atual`."
    ),
)
def update(
    meta_id: int,
    request: MetaCreate,
    usuario: CurrentUser,
    session: DbSession,
) -> MetaResponse:
    return service.update(session, usuario, meta_id, request)


@router.delete(
    "/{meta_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Excluir meta",
    description=(
        "Meta não tem vínculo com transação, então não há o bloqueio das "
        "RN08 e RN10 — a exclusão é direta e definitiva (R08)."
    ),
)
def delete(meta_id: int, usuario: CurrentUser, session: DbSession) -> Response:
    service.delete(session, usuario, meta_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
