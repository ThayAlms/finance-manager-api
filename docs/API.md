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
| `GET` | `/transacoes?inicio=AAAA-MM-DD&fim=AAAA-MM-DD` | Listar por período |
| `POST` | `/transacoes` | Criar transação |
| `GET` | `/transacoes/{id}` | Consultar transação |
| `PUT` | `/transacoes/{id}` | Atualizar transação |
| `DELETE` | `/transacoes/{id}` | Excluir transação |
| `GET` | `/metas` | Listar metas e progresso |
| `POST` | `/metas` | Criar meta |
| `GET` | `/metas/{id}` | Consultar meta |
| `PUT` | `/metas/{id}` | Atualizar meta |
| `DELETE` | `/metas/{id}` | Excluir meta |

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
