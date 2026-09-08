from fastapi import APIRouter, status

from app.core.database import DbSession
from app.core.security import CurrentUser
from app.schemas import UsuarioCreate, UsuarioResponse, UsuarioUpdate
from app.services import user as service

router = APIRouter(prefix="/usuarios", tags=["Usuários"])


@router.post(
    "",
    response_model=UsuarioResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cadastrar usuário",
    description=(
        "**Único endpoint público da API.** Todos os demais exigem o token "
        "obtido em `POST /auth/login`.\n\n"
        "A senha é guardada apenas como hash bcrypt, em `senha_hash` (RN03). "
        "O schema de resposta **não declara o campo senha** — assim é "
        "impossível vazá-la por esquecimento, seja no corpo da resposta, no "
        "log do servidor ou no print do Swagger.\n\n"
        "O e-mail é único e a comparação ignora maiúsculas (RN02): `Maria@x.com` "
        "e `maria@x.com` são o mesmo login. Duplicata responde `409`. A "
        "garantia real é o índice único sobre `lower(email)` no banco — "
        "verificar antes de inserir tem janela de corrida, e dois cadastros "
        "simultâneos passariam os dois pela checagem."
    ),
)
def create(request: UsuarioCreate, session: DbSession) -> UsuarioResponse:
    return service.create(session, request)


@router.get(
    "/me",
    response_model=UsuarioResponse,
    summary="Consultar perfil autenticado",
    description=(
        "O usuário vem sempre do token, nunca de um id na URL. Por isso a "
        "rota é `/me` e não `/usuarios/{id}`: não existe caminho na API para "
        "pedir o perfil de outra pessoa (RN01)."
    ),
)
def get_me(usuario: CurrentUser) -> UsuarioResponse:
    return service.response(usuario)


@router.put(
    "/me",
    response_model=UsuarioResponse,
    summary="Atualizar perfil autenticado",
    description=(
        "Altera nome e e-mail. A unicidade do e-mail (RN02) vale aqui "
        "também: mudar para um e-mail já cadastrado responde `409`.\n\n"
        "A senha não é alterada por este endpoint — troca de senha exige "
        "confirmar a senha atual e ficou para a próxima versão, junto da "
        "recuperação de senha (R05)."
    ),
)
def update_me(
    request: UsuarioUpdate, usuario: CurrentUser, session: DbSession
) -> UsuarioResponse:
    return service.update(session, usuario, request)
