from fastapi import APIRouter, Response, status

from app.core.database import DbSession
from app.core.security import CurrentUser
from app.schemas import CategoriaCreate, CategoriaResponse
from app.services import category as service

router = APIRouter(prefix="/categorias", tags=["Categorias"])


@router.get(
    "",
    response_model=list[CategoriaResponse],
    summary="Listar categorias visíveis",
    description=(
        "Devolve as categorias de sistema **mais** as personalizadas do "
        "usuário (RN16). As de sistema vêm do seed, têm `usuario_id` nulo, "
        "são compartilhadas por todos e aparecem com `sistema: true`.\n\n"
        "Elas existem para que um usuário recém-cadastrado consiga lançar a "
        "primeira despesa sem antes ter que criar categoria."
    ),
)
def list_all(usuario: CurrentUser, session: DbSession) -> list[CategoriaResponse]:
    return service.list_all(session, usuario)


@router.get(
    "/{categoria_id}",
    response_model=CategoriaResponse,
    summary="Consultar categoria",
    description=(
        "Alcança as categorias de sistema e as do próprio usuário. Categoria "
        "personalizada de outro usuário responde `404` (RN01)."
    ),
)
def find(
    categoria_id: int, usuario: CurrentUser, session: DbSession
) -> CategoriaResponse:
    return service.response(service.find(session, categoria_id, usuario))


@router.post(
    "",
    response_model=CategoriaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar categoria pessoal",
    description=(
        "O par `nome` + `tipo` é único por usuário (RN15) e a comparação "
        "ignora maiúsculas: com duas categorias \"Transporte\" de despesa, o "
        "gasto do mês apareceria rachado em duas linhas e nenhuma mostraria o "
        "total real. Duplicata responde `409`.\n\n"
        "O mesmo nome em tipos diferentes é permitido: \"Transporte\" como "
        "despesa (combustível) e como receita (o frete cobrado do cliente) "
        "são coisas diferentes na vida do autônomo."
    ),
)
def create(
    request: CategoriaCreate, usuario: CurrentUser, session: DbSession
) -> CategoriaResponse:
    return service.create(session, usuario, request)


@router.put(
    "/{categoria_id}",
    response_model=CategoriaResponse,
    summary="Atualizar categoria pessoal",
    description=(
        "Categoria de sistema responde `403` (RN09). Aqui o `403` é o código "
        "certo, e não o `404` da RN01: o recurso é público, o usuário sabe "
        "que ele existe, o que falta é permissão.\n\n"
        "A restrição existe porque a categoria de sistema é **uma linha só, "
        "compartilhada**: quem renomeasse \"Alimentação\" para \"Rango\" "
        "renomearia para todos os outros usuários. Quem quer nome próprio "
        "cria uma categoria pessoal."
    ),
)
def update(
    categoria_id: int,
    request: CategoriaCreate,
    usuario: CurrentUser,
    session: DbSession,
) -> CategoriaResponse:
    return service.update(session, usuario, categoria_id, request)


@router.delete(
    "/{categoria_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Excluir categoria pessoal sem transações",
    description=(
        "Dois bloqueios distintos:\n\n"
        "- categoria de sistema responde `403` (RN09) — o `ON DELETE "
        "RESTRICT` não cobriria esse caso, porque uma categoria do seed ainda "
        "sem uso seria apagada sem erro nenhum;\n"
        "- categoria com transação vinculada responde `409`, informando "
        "quantas (RN08). O usuário precisa reclassificar antes."
    ),
)
def delete(
    categoria_id: int, usuario: CurrentUser, session: DbSession
) -> Response:
    service.delete(session, usuario, categoria_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
