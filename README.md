# CaixaLivre API

API REST de gestão financeira para autônomos, freelancers e MEIs, desenvolvida em Python com FastAPI. O sistema separa finanças pessoais e do negócio e oferece controle de contas, categorias, transações e metas.

> Projeto em construção.

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
transações com filtro por período e tipo, define metas de economia e consulta
um resumo do mês. O saldo nunca é um valor guardado em coluna: é sempre
calculado a partir do histórico, para que não exista a possibilidade de
divergir do extrato.

Detalhes em [docs/escopo.md](docs/escopo.md).

## Entregas

- [CP1 — 01/09/2026](CP1/README.md)
- [CP2 — 06/10/2026](CP2/README.md)
- [CP3 — 27/10/2026](CP3/README.md)

## Stack

- Python 3.12, FastAPI e Uvicorn;
- SQLAlchemy 2 e Alembic;
- PostgreSQL 16;
- Pydantic, JWT e BCrypt;
- Pytest e HTTPX;
- Docker e Docker Compose.

## Estrutura

```text
app/
├── core/          configurações, banco, autenticação e erros
├── models/        entidades e enums
├── repositories/ consultas ao banco
├── routers/       endpoints HTTP
├── schemas/       contratos de entrada e saída
├── services/      regras de negócio
└── main.py        criação da aplicação
alembic/           migrações e carga inicial
tests/             testes automatizados
docs/              regras, modelo de dados e API
CP1, CP2, CP3/     listas de cada entrega
```

## Como executar

O arquivo [COMANDOS.txt](COMANDOS.txt) explica cada comando. A forma mais simples é:

```bash
docker compose up --build
```

Endereços locais:

- API: `http://localhost:8000`
- Swagger UI: `http://localhost:8000/docs`
- OpenAPI JSON: `http://localhost:8000/openapi.json`
- Saúde da aplicação: `http://localhost:8000/health`

## Documentação

- [Escopo](docs/escopo.md)
- [Regras de negócio](docs/regras-de-negocio.md)
- [Modelo de dados](docs/modelo-dados.md)
- [Diagrama entidade-relacionamento (DER)](docs/der.png)
- [Endpoints e exemplos](docs/API.md)
- [Decisões da integração](docs/DECISOES_DE_INTEGRACAO.md)
- [Checklist da CP1](docs/CHECKLIST_ENTREGA.md)

## Segurança e isolamento

O cadastro é público. Os demais recursos exigem o token JWT obtido em `POST /api/v1/auth/login`. O usuário é identificado pelo token; IDs de usuário enviados manualmente não são aceitos nos contratos financeiros.

## Banco

O PostgreSQL é versionado pelo Alembic. Na inicialização pelo Docker, `alembic upgrade head` cria as tabelas, índices, restrições e categorias padrão antes de iniciar a API.

## Testes

```bash
pytest -q
```

Os testes cobrem autenticação, isolamento entre usuários, regras das transações, saldo calculado, erros e contrato OpenAPI.

## Integrantes

| Integrante | RM |
|---|---|
| Thainá Almeida Santos | 569110 |
| Vitor Barbosa Vitorino | 570475 |
| Silvio Dela Libera Neto | 572632 |
