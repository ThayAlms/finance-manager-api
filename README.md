# CaixaLivre

Gestão financeira para autônomos, freelancers e MEIs.

> Projeto em construção — CP1 (FIAP). README completo entra no card
> "README do projeto" (ver [docs/TRELLO.md](docs/TRELLO.md)).

## Stack

Python + FastAPI + SQLAlchemy 2 + Alembic + PostgreSQL.

## Documentação

- [Modelo de dados (DER)](docs/modelo-dados.md)
- [Regras de negócio](docs/regras-de-negocio.md)
- [Quadro Trello e cards do CP1](docs/TRELLO.md)

## Rodando localmente

```bash
python -m venv .venv
.venv\Scripts\activate      # Windows
pip install -r requirements.txt
cp .env.example .env        # ajuste as variáveis se necessário
uvicorn app.main:app --reload
```

API em `http://localhost:8000`, documentação Swagger em `http://localhost:8000/docs`.
