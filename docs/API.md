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
| `GET` | `/transacoes` | Listar transações, com filtros opcionais |
| `POST` | `/transacoes` | Criar transação |
| `GET` | `/transacoes/{id}` | Consultar transação |
| `PUT` | `/transacoes/{id}` | Atualizar transação |
| `DELETE` | `/transacoes/{id}` | Excluir transação |
| `GET` | `/metas` | Listar metas e progresso |
| `POST` | `/metas` | Criar meta |
| `GET` | `/metas/{id}` | Consultar meta |
| `PUT` | `/metas/{id}` | Atualizar meta |
| `DELETE` | `/metas/{id}` | Excluir meta |
| `GET` | `/resumo?mes=MM&ano=AAAA` | Resumo do mês, com quebra PESSOAL/NEGOCIO |

## Filtros da listagem de transações

Todos opcionais e acumulativos. Sem nenhum, `GET /transacoes` devolve o
histórico completo.

| Parâmetro | Valores | Efeito |
|---|---|---|
| `inicio` | `AAAA-MM-DD` | Primeiro dia do período, inclusive |
| `fim` | `AAAA-MM-DD` | Último dia do período, inclusive |
| `tipo` | `RECEITA` ou `DESPESA` | Recorta pelo tipo do lançamento |
| `natureza` | `PESSOAL` ou `NEGOCIO` | Recorta pela natureza **da transação** |

```http
GET /transacoes?inicio=2026-08-01&fim=2026-08-31&tipo=DESPESA&natureza=NEGOCIO
```

`inicio` posterior a `fim` responde `422`. Valor fora do enum também responde
`422`, antes de chegar ao banco.

**Por que `natureza` filtra pela transação e não pela conta.** É o mesmo
critério que o `/resumo` usa em receitas e despesas. Filtrar por `NEGOCIO`
aqui devolve exatamente o conjunto que soma o `total_despesas` do negócio no
resumo — inclusive a despesa do negócio paga pela conta pessoal (RN14). Se o
filtro seguisse a conta, os dois números não fechariam, e o usuário não teria
como auditar o próprio resumo.

## Resumo do mês

`GET /resumo` sem parâmetro nenhum responde pelo mês corrente. `mes` e `ano`
são opcionais.

```json
{
  "mes": 9,
  "ano": 2026,
  "inicio": "2026-09-01",
  "fim": "2026-09-30",
  "saldo_total": "3550.00",
  "total_receitas": "800.00",
  "total_despesas": "250.00",
  "economia": "550.00",
  "quantidade_transacoes": 3,
  "por_natureza": [
    {
      "natureza": "PESSOAL",
      "saldo_contas": "750.00",
      "total_receitas": "0.00",
      "total_despesas": "150.00",
      "economia": "-150.00"
    },
    {
      "natureza": "NEGOCIO",
      "saldo_contas": "2800.00",
      "total_receitas": "800.00",
      "total_despesas": "100.00",
      "economia": "700.00"
    }
  ]
}
```

**Por que saldo e despesa não usam o mesmo critério.** `saldo_contas` agrupa
pela natureza da **conta**; `total_receitas` e `total_despesas` agrupam pela
natureza da **transação**. Pela RN14 uma despesa do negócio pode ser paga pela
conta pessoal — no exemplo acima, os 100,00 de despesa do negócio saíram da
conta pessoal. O saldo pessoal cai porque o dinheiro saiu de lá; a despesa
conta como do negócio porque é a ele que ela pertence. Somar os dois pelo mesmo
campo esconderia exatamente a mistura que o CaixaLivre existe para mostrar.

`saldo_total` e `saldo_contas` são **acumulados** — todo o histórico, pela
RN07. Só receitas, despesas e economia respeitam o período.

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
