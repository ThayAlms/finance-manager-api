from fastapi import APIRouter, Response, status

from app.core.database import DbSession
from app.core.security import CurrentUser
from app.schemas import ContaCreate, ContaResponse, ContaUpdate
from app.services import account as service

router = APIRouter(prefix="/contas", tags=["Contas"])


@router.get(
    "",
    response_model=list[ContaResponse],
    summary="Listar contas e saldos",
    description=(
        "Devolve as contas do usuário autenticado, ordenadas por nome.\n\n"
        "O campo `saldo_atual` **não é lido de nenhuma coluna**: é calculado a "
        "cada consulta como `saldo_inicial + receitas − despesas` da conta "
        "(RN07). Saldo guardado em coluna precisa ser atualizado na criação, "
        "edição e exclusão de transação, e um caminho esquecido faz o saldo "
        "divergir do extrato sem ninguém perceber."
    ),
)
def list_all(usuario: CurrentUser, session: DbSession) -> list[ContaResponse]:
    return service.list_all(session, usuario)


@router.get(
    "/{conta_id}",
    response_model=ContaResponse,
    summary="Consultar conta e saldo",
    description=(
        "Conta de outro usuário responde `404`, não `403` (RN01). Devolver "
        "`403` confirmaria que o recurso existe e permitiria descobrir ids "
        "alheios por tentativa — para quem não é dono, a conta não existe."
    ),
)
def find(conta_id: int, usuario: CurrentUser, session: DbSession) -> ContaResponse:
    return service.response(session, service.find(session, conta_id, usuario))


@router.post(
    "",
    response_model=ContaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar conta",
    description=(
        "Cria uma conta para o usuário do token. O dono nunca vem do corpo da "
        "requisição, sempre do JWT (RN01).\n\n"
        "`natureza` é obrigatória e define se a conta é PESSOAL ou NEGOCIO "
        "(RN14) — é o recorte que sustenta o produto.\n\n"
        "Nome repetido no mesmo usuário responde `409`, sem diferenciar "
        "maiúsculas de minúsculas."
    ),
)
def create(
    request: ContaCreate, usuario: CurrentUser, session: DbSession
) -> ContaResponse:
    return service.create(session, usuario, request)


@router.put(
    "/{conta_id}",
    response_model=ContaResponse,
    summary="Atualizar conta",
    description=(
        "Altera nome, tipo e natureza. **`saldo_inicial` não entra no corpo "
        "de propósito:** mudá-lo reescreveria retroativamente todo o saldo da "
        "conta sem deixar rastro no extrato. Para corrigir o valor de "
        "abertura, o caminho é lançar uma transação de ajuste."
    ),
)
def update(
    conta_id: int,
    request: ContaUpdate,
    usuario: CurrentUser,
    session: DbSession,
) -> ContaResponse:
    return service.update(session, usuario, conta_id, request)


@router.delete(
    "/{conta_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Excluir conta sem transações",
    description=(
        "Conta com transação vinculada responde `409`, informando quantas "
        "(RN10). Excluir em cascata apagaria o histórico financeiro do "
        "usuário sem aviso; o correto é ele mover ou apagar as transações "
        "antes. A garantia final é o `ON DELETE RESTRICT` da FK."
    ),
)
def delete(conta_id: int, usuario: CurrentUser, session: DbSession) -> Response:
    service.delete(session, usuario, conta_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
