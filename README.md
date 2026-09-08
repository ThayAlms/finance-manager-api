# CaixaLivre API

API REST de gestão financeira para autônomos, freelancers e MEIs, desenvolvida
em Python com FastAPI. O sistema separa finanças pessoais e do negócio e
oferece controle de contas, categorias, transações, metas e resumo mensal.

## O problema

Quem trabalha por conta própria costuma usar a mesma conta e o mesmo controle
para o dinheiro da pessoa e o do negócio — quando existe algum controle. Daí
não sai resposta para pergunta nenhuma: quanto sobrou do mês, quanto veio do
negócio, quanto já foi guardado para uma meta. App genérico de finanças não
resolve, porque não tem onde registrar essa separação.

## A solução

Uma API REST em que **toda conta e toda transação é marcada como PESSOAL ou
NEGOCIO** — é esse recorte que sustenta o produto. Em cima disso, o usuário
cadastra contas, classifica receitas e despesas por categoria, registra
transações com filtro por período, tipo e natureza, define metas de economia e
consulta o resumo do mês.

O saldo nunca é um valor guardado em coluna: é sempre calculado a partir do
histórico, para que não exista a possibilidade de divergir do extrato.

Detalhes em [docs/escopo.md](docs/escopo.md).

## Integrantes

| Integrante | RM |
|---|---|
| Thainá Almeida Santos | 569110 |
| Vitor Barbosa Vitorino | 570475 |
| Silvio Dela Libera Neto | 572632 |

## Planejamento

O acompanhamento das tarefas fica no Trello:
**[Controle Financeiro — CPs](https://trello.com/b/9r4U0gNO/controle-financeiro-cps)**

## Tecnologias

| Camada | Tecnologia |
|---|---|
| Linguagem | Python 3.12 |
| Framework web | FastAPI + Uvicorn |
| ORM e migrações | SQLAlchemy 2 + Alembic |
| Banco de dados | PostgreSQL 16 |
| Validação e contratos | Pydantic v2 |
| Autenticação | JWT (PyJWT) + BCrypt |
| Testes | Pytest + HTTPX |
| Empacotamento | Docker e Docker Compose |
| Integração contínua | GitHub Actions |

## Arquitetura

A aplicação é dividida em camadas, e cada requisição atravessa sempre a mesma
sequência:

```text
HTTP  ->  router  ->  service  ->  repository  ->  model  ->  PostgreSQL
                         ^
                      schema (valida a entrada e monta a saída)
```

| Camada | Responsabilidade | O que não faz |
|---|---|---|
| `routers/` | Declara rota, método, códigos HTTP e documentação | Não decide regra de negócio |
| `services/` | Aplica as regras de negócio e orquestra a transação | Não monta SQL |
| `repositories/` | Consultas e agregações no banco | Não conhece HTTP |
| `schemas/` | Contrato de entrada e saída, com validação Pydantic | Não acessa o banco |
| `models/` | Tabelas, colunas, constraints e índices | Não contém regra de aplicação |
| `core/` | Configuração, conexão, segurança e tratamento de erros | — |

A separação existe para que cada regra tenha **um lugar só**. O saldo é
calculado no repository e usado pelo service; a rota apenas devolve. Trocar o
banco mexeria em `repositories/` e `models/`, sem tocar nas regras de negócio.

```text
app/
├── core/          configuração, banco, autenticação e erros
├── models/        entidades e enums
├── repositories/  consultas ao banco
├── routers/       endpoints HTTP
├── schemas/       contratos de entrada e saída
├── services/      regras de negócio
└── main.py        criação da aplicação
alembic/           migrações e carga inicial
tests/             testes automatizados
docs/              regras, modelo de dados e API
CP1, CP2, CP3/     listas de cada entrega
```

## Instalação e execução

Pré-requisitos: **Git** e **Docker Desktop**. Para o modo local, também
**Python 3.12+**.

### Opção A — Docker (recomendada)

Sobe banco e API juntos, aplica as migrações e carrega as categorias padrão.

```bash
git clone https://github.com/ThayAlms/finance-manager-api.git
```

```bash
cd finance-manager-api
```

```bash
docker compose up --build
```

Não é preciso criar `.env`: o `compose.yaml` já define os valores de
desenvolvimento.

### Opção B — Python local, banco no Docker

```bash
python -m venv .venv
```

```bash
.venv\Scripts\activate
```

```bash
python -m pip install -r requirements.txt
```

```bash
copy .env.example .env
```

```bash
docker compose up -d postgres
```

```bash
alembic upgrade head
```

```bash
uvicorn app.main:app --reload
```

No Linux ou macOS, troque a ativação por `source .venv/bin/activate` e o
`copy` por `cp`.

O arquivo [COMANDOS.txt](COMANDOS.txt) explica cada comando um a um, incluindo
como parar os serviços e como recriar o banco do zero.

### Endereços locais

| Recurso | URL |
|---|---|
| API | `http://localhost:8000` |
| Swagger UI | `http://localhost:8000/docs` |
| ReDoc | `http://localhost:8000/redoc` |
| OpenAPI JSON | `http://localhost:8000/openapi.json` |
| Saúde da aplicação | `http://localhost:8000/health` |

## Variáveis de ambiente

Copie [.env.example](.env.example) para `.env` e ajuste o necessário. No modo
Docker elas já vêm definidas no `compose.yaml`.

| Variável | Padrão | Para que serve |
|---|---|---|
| `APP_NAME` | `CaixaLivre API` | Título exibido no Swagger |
| `ENVIRONMENT` | `development` | Identifica o ambiente em execução |
| `DATABASE_URL` | `postgresql+psycopg://caixalivre:caixalivre@localhost:5432/caixalivre` | Conexão com o PostgreSQL |
| `SECRET_KEY` | `development-only-change-me` | Assina os tokens JWT. **Troque fora de desenvolvimento** |
| `ALGORITHM` | `HS256` | Algoritmo de assinatura do JWT |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `60` | Validade do token, em minutos |

O `compose.yaml` aceita ainda `POSTGRES_DB`, `POSTGRES_USER`,
`POSTGRES_PASSWORD`, `POSTGRES_PORT` e `API_PORT`, para quem já usa a porta
5432 ou a 8000 em outra coisa.

## Banco de dados

**PostgreSQL 16**, versionado pelo Alembic. Na inicialização pelo Docker,
`alembic upgrade head` cria tabelas, índices, restrições e as categorias
padrão antes de a API subir.

Cinco entidades: `usuario`, `conta`, `categoria`, `transacao` e `meta`.

- `usuario` **1:N** `conta`, `categoria` (as personalizadas) e `meta`;
- `conta` **1:N** `transacao` — é esse vínculo que permite calcular o saldo;
- `categoria` **1:N** `transacao`.

`transacao` não guarda `usuario_id`: o dono é alcançado por
`transacao -> conta -> usuario`. Repetir o campo criaria dependência
transitiva (3ª Forma Normal) e permitiria que a mesma transação tivesse dois
donos diferentes conforme o caminho da consulta.

Diagrama em [docs/der.png](docs/der.png); colunas, tipos e constraints em
[docs/modelo-dados.md](docs/modelo-dados.md).

## Principais endpoints

Base: `http://localhost:8000/api/v1`. Todos exigem
`Authorization: Bearer SEU_TOKEN`, exceto o cadastro e o login.

| Método | Endpoint | Operação |
|---|---|---|
| `POST` | `/usuarios` | Cadastrar usuário (público) |
| `POST` | `/auth/login` | Obter token JWT (público) |
| `GET` `PUT` | `/usuarios/me` | Consultar e atualizar o perfil |
| `GET` `POST` | `/categorias` | Listar (sistema + pessoais) e criar |
| `GET` `PUT` `DELETE` | `/categorias/{id}` | Consultar, atualizar e excluir |
| `GET` `POST` | `/contas` | Listar com saldo calculado e criar |
| `GET` `PUT` `DELETE` | `/contas/{id}` | Consultar, atualizar e excluir |
| `GET` `POST` | `/transacoes` | Listar com filtros e registrar |
| `GET` `PUT` `DELETE` | `/transacoes/{id}` | Consultar, atualizar e excluir |
| `GET` `POST` | `/metas` | Listar com progresso e criar |
| `GET` `PUT` `DELETE` | `/metas/{id}` | Consultar, atualizar e excluir |
| `GET` | `/resumo` | Resumo do mês, com quebra PESSOAL/NEGOCIO |

A listagem de transações aceita quatro filtros opcionais e acumulativos:

```http
GET /transacoes?inicio=2026-08-01&fim=2026-08-31&tipo=DESPESA&natureza=NEGOCIO
```

Tabela completa, exemplos de corpo e formato de erro em
[docs/API.md](docs/API.md). Requisições prontas para o REST Client do VS Code
em [docs/requests.http](docs/requests.http).

## Documentação Swagger

Com a API em execução, a documentação interativa fica em
**`http://localhost:8000/docs`**.

Todos os endpoints trazem descrição, parâmetros, exemplos de corpo e os
códigos HTTP possíveis. Para testar as rotas protegidas:

1. cadastre-se em `POST /usuarios`;
2. obtenha o token em `POST /auth/login`;
3. clique em **Authorize**, cole o `access_token` e feche o diálogo;
4. use o **Try it out** de qualquer endpoint.

## Segurança e isolamento

O cadastro é público; os demais recursos exigem o token JWT. O usuário é
sempre identificado pelo token — IDs de usuário enviados manualmente não são
aceitos nos contratos financeiros. Recurso de outro usuário responde `404`, e
não `403`, para não confirmar a existência de ids alheios.

Senhas são guardadas apenas como hash bcrypt e nunca aparecem em resposta
alguma. Todos os valores monetários usam `NUMERIC(14,2)` no banco e `Decimal`
na aplicação — nunca `float`.

## Respostas de erro

Toda falha responde no mesmo formato:

```json
{
  "timestamp": "2026-09-07T18:00:00+00:00",
  "status": 422,
  "error": "Unprocessable Entity",
  "message": "A data da transação não pode estar no futuro",
  "path": "/api/v1/transacoes"
}
```

| Código | Quando acontece |
|---|---|
| `400` | JSON malformado |
| `401` | Token ausente, inválido ou expirado |
| `403` | Escrita em categoria de sistema |
| `404` | Recurso inexistente ou de outro usuário |
| `409` | Duplicidade ou vínculo que impede a exclusão |
| `422` | Campo ou regra de negócio violada |

## Testes

```bash
pytest -q
```

Cobrem autenticação, isolamento entre usuários, regras das transações, saldo
calculado, filtros, resumo mensal, erros e a qualidade do contrato OpenAPI. O
GitHub Actions roda a suíte contra um PostgreSQL real a cada push.

## Documentação do projeto

- [Escopo](docs/escopo.md) — problema, público-alvo, entidades e restrições
- [Regras de negócio](docs/regras-de-negocio.md) — RN01 a RN17, com o porquê de cada uma
- [Modelo de dados](docs/modelo-dados.md) — colunas, tipos, constraints e índices
- [Diagrama entidade-relacionamento](docs/der.png)
- [Endpoints e exemplos](docs/API.md)
- [Decisões da integração](docs/DECISOES_DE_INTEGRACAO.md)
- [Checklist da CP1](docs/CHECKLIST_ENTREGA.md)
- [Comandos de execução](COMANDOS.txt)

## Entregas

- [CP1 — 01/09/2026](CP1/README.md)
- [CP2 — 06/10/2026](CP2/README.md)
- [CP3 — 27/10/2026](CP3/README.md)
