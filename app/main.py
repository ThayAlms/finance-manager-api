from fastapi import FastAPI

from app.core.config import settings
from app.core.errors import register_exception_handlers
from app.routers import (
    accounts,
    auth,
    categories,
    goals,
    health,
    summary,
    transactions,
    users,
)
from app.schemas.common import COMMON_RESPONSES

DESCRIPTION = """
API REST de gestão financeira para autônomos, freelancers e MEIs.

**O recorte do produto:** toda conta e toda transação é marcada como
`PESSOAL` ou `NEGOCIO`. É o que responde a pergunta que um app genérico de
finanças não responde — quanto do que sobrou no mês é do negócio e quanto é
da pessoa.

### Como usar esta documentação

1. Cadastre-se em `POST /api/v1/usuarios` — é o único endpoint público.
2. Troque e-mail e senha por um token em `POST /api/v1/auth/login`.
3. Clique em **Authorize**, cole o `access_token` e feche o diálogo.
4. A partir daí todos os endpoints respondem no contexto do seu usuário.

### Duas decisões que aparecem em toda a API

**Valores calculados, nunca armazenados.** Saldo da conta, progresso da meta e
os totais do resumo são derivados do histórico a cada leitura (RN07, RN11 e
RN12). Coluna derivada precisa ser atualizada em todo caminho de escrita, e um
esquecido faz o número divergir da origem sem erro nenhum.

**Recurso de outro usuário responde `404`, não `403`.** Devolver `403`
confirmaria que o recurso existe e permitiria mapear ids alheios por tentativa
(RN01). A exceção é a categoria de sistema, que é pública e por isso responde
`403` na tentativa de escrita (RN09).

### Formato dos erros

Toda falha responde o mesmo corpo, com `timestamp`, `status`, `error`,
`message` e `path` — e `fieldErrors` quando a falha é de validação de campo.
O detalhe de cada código está em **Respostas** dentro de cada endpoint.
"""

TAGS = [
    {
        "name": "Saúde",
        "description": "Verificação de que a API e o banco estão respondendo.",
    },
    {
        "name": "Autenticação",
        "description": "Obtenção do token JWT. **Comece por aqui.**",
    },
    {
        "name": "Usuários",
        "description": (
            "Cadastro e perfil. O cadastro é público; o perfil sempre vem do "
            "token, nunca de um id na URL."
        ),
    },
    {
        "name": "Categorias",
        "description": (
            "Classificação de receitas e despesas. As de sistema vêm do seed "
            "e são compartilhadas por todos (RN16); as personalizadas são do "
            "usuário."
        ),
    },
    {
        "name": "Contas",
        "description": (
            "Onde o dinheiro fica, com natureza PESSOAL ou NEGOCIO. O saldo é "
            "sempre calculado a partir do histórico (RN07)."
        ),
    },
    {
        "name": "Transações",
        "description": (
            "O lançamento em si — receita ou despesa. Concentra a maior parte "
            "das regras de negócio."
        ),
    },
    {
        "name": "Metas",
        "description": (
            "Objetivos de economia, com progresso e conclusão calculados na "
            "leitura (RN11 e RN12)."
        ),
    },
    {
        "name": "Resumo",
        "description": (
            "A fotografia do mês, com a quebra entre pessoal e negócio que é "
            "o diferencial do CaixaLivre."
        ),
    },
]

app = FastAPI(
    title=settings.app_name,
    description=DESCRIPTION,
    version="1.0.0",
    contact={"name": "Equipe CaixaLivre"},
    license_info={"name": "Uso acadêmico — FIAP"},
    openapi_tags=TAGS,
    servers=[{"url": "http://localhost:8000", "description": "Ambiente local"}],
)

register_exception_handlers(app)

app.include_router(health.router)

for api_router in (
    auth.router,
    users.router,
    categories.router,
    accounts.router,
    transactions.router,
    goals.router,
    summary.router,
):
    app.include_router(
        api_router,
        prefix="/api/v1",
        responses=COMMON_RESPONSES,
    )
