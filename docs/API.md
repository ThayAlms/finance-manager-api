# Contrato e demonstração da API

Base local: `http://localhost:8080/api/v1`

Documentação interativa: `http://localhost:8080/swagger-ui.html`

Contrato OpenAPI em JSON: `http://localhost:8080/v3/api-docs`

## Recursos

| Recurso | Rota | Operações |
|---|---|---|
| Usuários | `/users` | listar, consultar, criar, atualizar e excluir |
| Categorias | `/categories` | listar por usuário, consultar, criar, atualizar e excluir |
| Contas | `/accounts` | listar por usuário, consultar, criar, atualizar e excluir |
| Transações | `/transactions` | listar por usuário/período, consultar, criar, atualizar e excluir |
| Metas | `/goals` | listar por usuário, consultar, criar, atualizar e excluir |

## Sequência de demonstração

1. Crie um usuário e guarde o `id` retornado.
2. Crie uma categoria usando o `userId`.
3. Crie uma conta usando o mesmo `userId`.
4. Crie uma transação `COMPLETED` usando os três identificadores.
5. Consulte a conta e confira a atualização do saldo.
6. Atualize a transação para `CANCELLED` e confira a reversão do saldo.
7. Tente excluir a conta e observe a resposta `409`, pois existe uma transação vinculada.

O arquivo [`requests.http`](requests.http) contém as requisições prontas para clientes compatíveis com HTTP Client. O Swagger também permite executar o roteiro pelo navegador.

## Formato de erro

```json
{
  "timestamp": "2026-09-03T12:00:00-03:00",
  "status": 400,
  "error": "Bad Request",
  "message": "Existem campos inválidos na requisição",
  "path": "/api/v1/users",
  "fieldErrors": {
    "email": "deve ser um endereço de e-mail bem formado"
  }
}
```

Os valores possíveis dos enums e os schemas completos de entrada e saída estão publicados no contrato OpenAPI.
