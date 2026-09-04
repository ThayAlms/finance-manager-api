# CaixaLivre

Gestão financeira para autônomos, freelancers e MEIs.

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

## Stack

Python + FastAPI + SQLAlchemy 2 + Alembic + PostgreSQL.

## Documentação

- [Escopo](docs/escopo.md)
- [Regras de negócio](docs/regras-de-negocio.md)
- [Modelo de dados](docs/modelo-dados.md)
- [Diagrama entidade-relacionamento (DER)](docs/der.png)

## Rodando localmente

```bash
python -m venv .venv
.venv\Scripts\activate      # Windows
pip install -r requirements.txt
cp .env.example .env        # ajuste as variáveis se necessário
uvicorn app.main:app --reload
```

API em `http://localhost:8000`, documentação Swagger em `http://localhost:8000/docs`.

## Integrantes

| Integrante | RM |
|---|---|
| Thainá Almeida Santos | 569110 |
| Vitor Barbosa Vitorino | 570475 |
| Silvio Dela Libera Neto | 572632 |
