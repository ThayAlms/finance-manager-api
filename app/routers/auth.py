from fastapi import APIRouter

from app.core.database import DbSession
from app.schemas import LoginRequest, TokenResponse
from app.services import auth as service

router = APIRouter(prefix="/auth", tags=["Autenticação"])


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Autenticar usuário",
    description=(
        "Troca e-mail e senha por um token JWT. Use o valor de "
        "`access_token` no botão **Authorize** do Swagger, ou no cabeçalho "
        "`Authorization: Bearer SEU_TOKEN`.\n\n"
        "E-mail inexistente e senha errada respondem o **mesmo** `401` com a "
        "mesma mensagem, de propósito: distinguir os dois casos permitiria "
        "descobrir quais e-mails estão cadastrados testando um por um.\n\n"
        "O token carrega o id do usuário e expira conforme "
        "`ACCESS_TOKEN_EXPIRE_MINUTES` (60 por padrão). É dele que sai o dono "
        "de toda conta, categoria, transação e meta (RN01)."
    ),
)
def login(request: LoginRequest, session: DbSession) -> TokenResponse:
    return service.login(session, request)
