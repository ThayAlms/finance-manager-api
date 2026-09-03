# CaixaLivre

Gestão financeira para autônomos, freelancers e MEIs.

> Projeto em construção — CP1 (FIAP).

## Stack

Python + FastAPI + SQLAlchemy 2 + Alembic + PostgreSQL.

## Documentação

- [Escopo](docs/escopo.md)
- [Regras de negócio](docs/regras-de-negocio.md)
- [Modelo de dados (DER)](docs/modelo-dados.md)

## Rodando localmente

```bash
python -m venv .venv
.venv\Scripts\activate      # Windows
pip install -r requirements.txt
cp .env.example .env        # ajuste as variáveis se necessário
uvicorn app.main:app --reload
```

API em `http://localhost:8000`, documentação Swagger em `http://localhost:8000/docs`.
