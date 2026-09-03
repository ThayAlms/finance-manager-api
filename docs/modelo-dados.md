# Modelo de dados — CaixaLivre

O schema está em 3ª Forma Normal: a transação não repete `usuario_id`, pois seu proprietário é determinado pela conta. O saldo atual também não é armazenado; ele é calculado pelas transações.

```mermaid
erDiagram
    USUARIO ||--o{ CONTA : possui
    USUARIO ||--o{ CATEGORIA : personaliza
    USUARIO ||--o{ META : define
    CONTA ||--o{ TRANSACAO : recebe
    CATEGORIA ||--o{ TRANSACAO : classifica

    USUARIO {
        bigint id PK
        varchar nome
        varchar email UK
        varchar senha_hash
        timestamptz criado_em
    }
    CONTA {
        bigint id PK
        bigint usuario_id FK
        varchar nome
        enum tipo
        enum natureza
        numeric saldo_inicial
    }
    CATEGORIA {
        bigint id PK
        bigint usuario_id FK "nulo para categoria do sistema"
        varchar nome
        enum tipo
    }
    TRANSACAO {
        bigint id PK
        bigint conta_id FK
        bigint categoria_id FK
        varchar descricao
        numeric valor
        date data
        enum tipo
        enum natureza
    }
    META {
        bigint id PK
        bigint usuario_id FK
        varchar nome
        numeric valor_meta
        numeric valor_atual
        date prazo
    }
```

## Integridade

- IDs numéricos gerados pelo PostgreSQL;
- e-mail único;
- conta única por usuário e nome;
- categoria personalizada única por usuário, nome e tipo;
- categorias do sistema únicas por nome e tipo;
- valores financeiros protegidos por `CHECK`;
- exclusão de conta ou categoria referenciada por transação é restrita;
- índices sustentam filtros por usuário, conta e período.

A definição executável está em `alembic/versions/0001_schema_inicial.py`.
