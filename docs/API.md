# API REST — CaixaLivre

Base local: `http://localhost:8000/api/v1`

Swagger: `http://localhost:8000/docs`

## Autenticação

1. Cadastre o usuário em `POST /usuarios`.
2. Envie e-mail e senha para `POST /auth/login`.
3. Use o token retornado como `Authorization: Bearer SEU_TOKEN`.

O usuário dos recursos financeiros é sempre obtido do token.

## Endpoints

| Método | Endpoint | Operação |
|---|---|---|
| `POST` | `/usuarios` | Cadastrar usuário |
| `GET` | `/usuarios/me` | Consultar perfil autenticado |
| `PUT` | `/usuarios/me` | Atualizar perfil autenticado |
| `POST` | `/auth/login` | Obter token JWT |
| `GET` | `/categorias` | Listar categorias do sistema e pessoais |
| `POST` | `/categorias` | Criar categoria pessoal |
| `GET` | `/categorias/{id}` | Consultar categoria |
| `PUT` | `/categorias/{id}` | Atualizar categoria pessoal |
| `DELETE` | `/categorias/{id}` | Excluir categoria sem transações |
| `GET` | `/contas` | Listar contas com saldo calculado |
| `POST` | `/contas` | Criar conta |
| `GET` | `/contas/{id}` | Consultar conta e saldo |
| `PUT` | `/contas/{id}` | Atualizar conta sem alterar saldo inicial |
| `DELETE` | `/contas/{id}` | Excluir conta sem transações |
| `GET` | `/transacoes?inicio=AAAA-MM-DD&fim=AAAA-MM-DD&tipo=DESPESA&natureza=PESSOAL&offset=0&limit=100` | Listar com filtros e paginação |
| `POST` | `/transacoes` | Criar transação |
| `GET` | `/transacoes/{id}` | Consultar transação |
| `PUT` | `/transacoes/{id}` | Atualizar transação |
| `DELETE` | `/transacoes/{id}` | Excluir transação |
| `GET` | `/metas` | Listar metas e progresso |
| `POST` | `/metas` | Criar meta |
| `GET` | `/metas/{id}` | Consultar meta |
| `PUT` | `/metas/{id}` | Atualizar meta |
| `DELETE` | `/metas/{id}` | Excluir meta |
| `GET` | `/resumo?inicio=AAAA-MM-DD&fim=AAAA-MM-DD` | Obter totais e séries do dashboard |
| `POST` | `/insights?inicio=AAAA-MM-DD&fim=AAAA-MM-DD` | Gerar análise financeira educativa |
| `POST` | `/extratos/preview` | Ler CSV/OFX e sugerir classificações sem gravar |
| `POST` | `/extratos/confirmar` | Gravar os lançamentos revisados e criar/reusar a conta |

## Resumo financeiro

`GET /resumo` devolve, para o período solicitado:

- saldo atual somando todas as contas;
- receitas, despesas, resultado e taxa de economia;
- totais separados por natureza `PESSOAL` e `NEGOCIO`;
- agrupamento por categoria;
- evolução mensal.

Todos os cálculos são limitados ao usuário identificado pelo JWT.

## Insights

`POST /insights` envia apenas o resumo agregado à Gemini API. Senha, token e lançamentos individuais não são enviados. Quando `GEMINI_API_KEY` não estiver configurada ou o provedor estiver indisponível, a resposta contém `gerado_por_ia: false` e uma análise local.

## Paginação de transações

Use `offset` e `limit` na listagem de transações. O cabeçalho de resposta `X-Total-Count` informa quantos registros correspondem aos filtros, antes da paginação.

## Importação inteligente de extratos

O fluxo ocorre em duas etapas:

1. `POST /extratos/preview` recebe conteúdo textual CSV, OFX ou QFX, normaliza os lançamentos e sugere natureza e categoria.
2. O usuário revisa as sugestões no frontend.
3. `POST /extratos/confirmar` cria ou reutiliza a conta e grava somente os itens confirmados.

Cada lançamento importado recebe um hash derivado de data, descrição e valor. O índice único por conta impede que o mesmo lançamento seja importado duas vezes. A IA nunca grava diretamente no banco.

## Exemplo de erro

```json
{
  "timestamp": "2026-09-03T18:00:00+00:00",
  "status": 422,
  "error": "Unprocessable Entity",
  "message": "A data da transação não pode estar no futuro",
  "path": "/api/v1/transacoes"
}
```

Requisições completas estão em [`requests.http`](requests.http).
