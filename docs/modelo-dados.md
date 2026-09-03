# Modelo de dados — CaixaLivre (CP1)

Entregável do card **Modelagem do banco de dados (DER)**.
Referência de regras: [regras-de-negocio.md](regras-de-negocio.md).

SGBD: PostgreSQL. ORM: SQLAlchemy 2. Migrations: Alembic.

---

## 1. Enums

Três enums nativos do Postgres. Enum em vez de `VARCHAR` livre porque o banco
passa a rejeitar valor inválido sozinho — não depende de ninguém lembrar de validar.

| Enum | Valores | Usado em |
|---|---|---|
| `tipo_movimento` | `RECEITA`, `DESPESA` | `categoria.tipo`, `transacao.tipo` |
| `tipo_conta` | `CORRENTE`, `POUPANCA`, `CARTEIRA` | `conta.tipo` |
| `natureza` | `PESSOAL`, `NEGOCIO` | `conta.natureza`, `transacao.natureza` |

`tipo_conta` **não** tem `CARTAO_CREDITO` — restrição R03. Cartão tem fatura,
limite e fechamento; não cabe na entidade Conta. Fica para o CP2.

---

## 2. Entidades e atributos

### `usuario`

| Coluna | Tipo | Restrições | Observação |
|---|---|---|---|
| `id` | BIGSERIAL | PK | |
| `nome` | VARCHAR(120) | NOT NULL | |
| `email` | VARCHAR(180) | NOT NULL, UNIQUE | RN02 |
| `senha_hash` | VARCHAR(255) | NOT NULL | RN03 — bcrypt, nunca em resposta |
| `criado_em` | TIMESTAMPTZ | NOT NULL, DEFAULT now() | |
| `atualizado_em` | TIMESTAMPTZ | NOT NULL, DEFAULT now() | |

### `conta`

| Coluna | Tipo | Restrições | Observação |
|---|---|---|---|
| `id` | BIGSERIAL | PK | |
| `usuario_id` | BIGINT | NOT NULL, FK → usuario | RN01 |
| `nome` | VARCHAR(80) | NOT NULL | |
| `tipo` | tipo_conta | NOT NULL | |
| `natureza` | natureza | NOT NULL | RN14 |
| `saldo_inicial` | NUMERIC(14,2) | NOT NULL, DEFAULT 0 | RN07, RN17 |
| `criado_em` | TIMESTAMPTZ | NOT NULL, DEFAULT now() | |
| `atualizado_em` | TIMESTAMPTZ | NOT NULL, DEFAULT now() | |

`UNIQUE (usuario_id, nome)` — o usuário não tem duas contas com o mesmo nome.

**Não existe coluna `saldo`.** RN07: o saldo é calculado na leitura.

### `categoria`

| Coluna | Tipo | Restrições | Observação |
|---|---|---|---|
| `id` | BIGSERIAL | PK | |
| `usuario_id` | BIGINT | **NULL**, FK → usuario | NULL = de sistema (RN16) |
| `nome` | VARCHAR(60) | NOT NULL | |
| `tipo` | tipo_movimento | NOT NULL | RN05 |
| `criado_em` | TIMESTAMPTZ | NOT NULL, DEFAULT now() | |
| `atualizado_em` | TIMESTAMPTZ | NOT NULL, DEFAULT now() | |

**Armadilha da RN15.** No Postgres, `UNIQUE` trata NULL como valor distinto —
um `UNIQUE (usuario_id, nome, tipo)` **não** impediria dez categorias de sistema
chamadas "Alimentação". A solução são dois índices parciais:

```sql
CREATE UNIQUE INDEX uq_categoria_sistema
  ON categoria (nome, tipo)
  WHERE usuario_id IS NULL;

CREATE UNIQUE INDEX uq_categoria_usuario
  ON categoria (usuario_id, nome, tipo)
  WHERE usuario_id IS NOT NULL;
```

### `transacao`

| Coluna | Tipo | Restrições | Observação |
|---|---|---|---|
| `id` | BIGSERIAL | PK | |
| `conta_id` | BIGINT | NOT NULL, FK → conta | Sem isso o saldo é impossível |
| `categoria_id` | BIGINT | NOT NULL, FK → categoria | |
| `descricao` | VARCHAR(160) | NOT NULL | |
| `valor` | NUMERIC(14,2) | NOT NULL, CHECK > 0 | RN04, RN17 |
| `data` | DATE | NOT NULL | RN13 |
| `tipo` | tipo_movimento | NOT NULL | RN05 |
| `natureza` | natureza | NOT NULL | RN14 |
| `criado_em` | TIMESTAMPTZ | NOT NULL, DEFAULT now() | |
| `atualizado_em` | TIMESTAMPTZ | NOT NULL, DEFAULT now() | |

**Não tem `usuario_id`.** Ver seção 3.

### `meta`

| Coluna | Tipo | Restrições | Observação |
|---|---|---|---|
| `id` | BIGSERIAL | PK | |
| `usuario_id` | BIGINT | NOT NULL, FK → usuario | |
| `nome` | VARCHAR(80) | NOT NULL | |
| `valor_meta` | NUMERIC(14,2) | NOT NULL, CHECK > 0 | RN11 |
| `valor_atual` | NUMERIC(14,2) | NOT NULL, DEFAULT 0, CHECK >= 0 | R07 — aporte manual |
| `prazo` | DATE | NULL | |
| `criado_em` | TIMESTAMPTZ | NOT NULL, DEFAULT now() | |
| `atualizado_em` | TIMESTAMPTZ | NOT NULL, DEFAULT now() | |

`progresso_percentual`, `valor_restante` e `atingida` **não são colunas** —
são calculados na leitura (RN11, RN12).

---

## 3. Relacionamentos e política de exclusão

| Origem | Destino | Cardinalidade | ON DELETE | Motivo |
|---|---|---|---|---|
| `conta.usuario_id` | `usuario.id` | N:1 | CASCADE | Não há endpoint de excluir usuário no CP1 |
| `categoria.usuario_id` | `usuario.id` | N:1 | CASCADE | Idem |
| `meta.usuario_id` | `usuario.id` | N:1 | CASCADE | Idem |
| `transacao.conta_id` | `conta.id` | N:1 | **RESTRICT** | RN10 |
| `transacao.categoria_id` | `categoria.id` | N:1 | **RESTRICT** | RN08 |

Leitura: um usuário tem N contas, N categorias personalizadas e N metas.
Uma conta tem N transações. Uma categoria classifica N transações.

### Por que `transacao` não tem `usuario_id`

O dono da transação é alcançável por `transacao → conta → usuario`. Repetir
`usuario_id` em `transacao` cria uma **dependência transitiva** — o valor passa
a ser determinado por `conta_id`, e isso viola a 3ª Forma Normal.

Dois motivos para não fazer:

1. **O CP2 avalia "normalização do banco" explicitamente.** Entrar no CP2 com
   uma violação de 3NF conhecida é entregar o problema de bandeja.
2. **Risco real de divergência.** Se alguém mover uma transação para outra conta
   e esquecer de atualizar `transacao.usuario_id`, a transação passa a pertencer
   a dois donos diferentes dependendo de por onde você consulta. É o mesmo tipo
   de bug que a RN07 evita no saldo.

Custo: a RN01 vira um join em vez de um filtro direto.

```sql
SELECT t.* FROM transacao t
JOIN conta c ON c.id = t.conta_id
WHERE c.usuario_id = :usuario_atual;
```

Com o índice `idx_conta_usuario` isso é irrelevante no volume do CP1.

---

## 4. Constraints e índices

### CHECK — regras garantidas pelo próprio banco

```sql
ALTER TABLE transacao ADD CONSTRAINT ck_transacao_valor_positivo
  CHECK (valor > 0);                              -- RN04

ALTER TABLE meta ADD CONSTRAINT ck_meta_valor_positivo
  CHECK (valor_meta > 0);                         -- RN11

ALTER TABLE meta ADD CONSTRAINT ck_meta_atual_nao_negativo
  CHECK (valor_atual >= 0);                       -- RN11
```

### Índices

```sql
CREATE INDEX idx_conta_usuario      ON conta (usuario_id);
CREATE INDEX idx_categoria_usuario  ON categoria (usuario_id);
CREATE INDEX idx_meta_usuario       ON meta (usuario_id);
CREATE INDEX idx_transacao_conta_data ON transacao (conta_id, data DESC);
CREATE INDEX idx_transacao_categoria  ON transacao (categoria_id);
CREATE INDEX idx_transacao_data       ON transacao (data);
```

`idx_transacao_conta_data` é o que sustenta o filtro por período (card 9) e o
cálculo de saldo (RN07) — as duas consultas mais usadas da aplicação.

### RN13 não vira CHECK

`data <= CURRENT_DATE` não pode ser CHECK: a expressão não é imutável, o
Postgres recusa. Fica no service, validada pelo Pydantic.

### RN05 — opcional, só se sobrar tempo

RN05 (tipo da transação = tipo da categoria) é uma regra entre duas tabelas.
O caminho normal é validar no service, e é isso que está previsto no card 9.

Existe uma forma de garantir no banco, com chave estrangeira composta:

```sql
ALTER TABLE categoria ADD CONSTRAINT uq_categoria_id_tipo UNIQUE (id, tipo);

ALTER TABLE transacao ADD CONSTRAINT fk_transacao_categoria_tipo
  FOREIGN KEY (categoria_id, tipo) REFERENCES categoria (id, tipo);
```

Como `transacao.tipo` precisa bater com `categoria.tipo` para a FK existir, o
banco passa a rejeitar sozinho uma despesa com categoria de receita.

É elegante e rende ponto em domínio técnico na apresentação, mas **não faça
antes do resto estar pronto** — não é obrigatório e adiciona complexidade na
migration.

---

## 5. Validação: cada regra contra o modelo

Este é o passo que fecha o card. Se alguma regra não tiver onde ser aplicada,
o modelo está errado — não a regra.

| Regra | Onde é garantida |
|---|---|
| RN01 — isolamento por usuário | FK `usuario_id` em conta/categoria/meta; join via conta para transação |
| RN02 — e-mail único | `UNIQUE (email)` |
| RN03 — senha só como hash | Coluna `senha_hash`; ausente no schema de saída |
| RN04 — valor > 0 | `CHECK (valor > 0)` |
| RN05 — tipo transação = tipo categoria | Service (ou FK composta, opcional) |
| RN06 — posse dos vínculos | Service, comparando `conta.usuario_id` com o JWT |
| RN07 — saldo calculado | Ausência da coluna `saldo` + agregação na leitura |
| RN08 — categoria com transação | FK `ON DELETE RESTRICT` |
| RN09 — categoria de sistema imutável | Service, checando `usuario_id IS NULL` |
| RN10 — conta com transação | FK `ON DELETE RESTRICT` |
| RN11 — meta válida e progresso | `CHECK (valor_meta > 0)` + cálculo na leitura |
| RN12 — meta atingida | Cálculo na leitura |
| RN13 — sem data futura | Service / Pydantic |
| RN14 — natureza obrigatória | Coluna `natureza` NOT NULL nas duas tabelas |
| RN15 — nome de categoria único | Dois índices parciais |
| RN16 — categorias de sistema | `usuario_id` anulável + seed |
| RN17 — moeda e precisão | `NUMERIC(14,2)` em todo valor |

Placar: **8 regras garantidas pelo banco, 9 pela aplicação.** Vale citar na
apresentação — mostra que a escolha de onde aplicar cada regra foi consciente.

---

## 6. Seed — categorias de sistema (RN16)

Todas com `usuario_id = NULL`.

**RECEITA:** Salário · Vendas · Serviços prestados · Investimentos · Outras receitas

**DESPESA:** Alimentação · Transporte · Moradia · Saúde · Educação · Lazer ·
Assinaturas · Impostos e taxas · Ferramentas e software · Outras despesas

"Impostos e taxas" e "Ferramentas e software" existem por causa do público-alvo
(autônomos e MEIs) — são as duas categorias que um app genérico não teria.

---

## 7. DBML para o diagrama

Cole em [dbdiagram.io](https://dbdiagram.io) → **New Diagram** → substitua o
conteúdo do editor. O diagrama é gerado na hora; exporte em PNG com
**Export → PNG** e salve como `docs/der.png`.

```dbml
Enum tipo_movimento {
  RECEITA
  DESPESA
}

Enum tipo_conta {
  CORRENTE
  POUPANCA
  CARTEIRA
}

Enum natureza {
  PESSOAL
  NEGOCIO
}

Table usuario {
  id bigserial [pk]
  nome varchar(120) [not null]
  email varchar(180) [not null, unique, note: 'RN02']
  senha_hash varchar(255) [not null, note: 'RN03 - bcrypt']
  criado_em timestamptz [not null, default: `now()`]
  atualizado_em timestamptz [not null, default: `now()`]
}

Table conta {
  id bigserial [pk]
  usuario_id bigint [not null]
  nome varchar(80) [not null]
  tipo tipo_conta [not null]
  natureza natureza [not null, note: 'RN14']
  saldo_inicial numeric(14,2) [not null, default: 0, note: 'RN07 - nao existe coluna saldo']
  criado_em timestamptz [not null, default: `now()`]
  atualizado_em timestamptz [not null, default: `now()`]

  Indexes {
    (usuario_id, nome) [unique]
    usuario_id
  }
}

Table categoria {
  id bigserial [pk]
  usuario_id bigint [null, note: 'NULL = categoria de sistema (RN16)']
  nome varchar(60) [not null]
  tipo tipo_movimento [not null]
  criado_em timestamptz [not null, default: `now()`]
  atualizado_em timestamptz [not null, default: `now()`]

  Indexes {
    (usuario_id, nome, tipo) [unique, note: 'RN15 - ver indices parciais']
    usuario_id
  }
}

Table transacao {
  id bigserial [pk]
  conta_id bigint [not null]
  categoria_id bigint [not null]
  descricao varchar(160) [not null]
  valor numeric(14,2) [not null, note: 'RN04 - CHECK valor > 0']
  data date [not null, note: 'RN13 - nao pode ser futura']
  tipo tipo_movimento [not null, note: 'RN05 - deve bater com categoria.tipo']
  natureza natureza [not null, note: 'RN14']
  criado_em timestamptz [not null, default: `now()`]
  atualizado_em timestamptz [not null, default: `now()`]

  Indexes {
    (conta_id, data)
    categoria_id
    data
  }
}

Table meta {
  id bigserial [pk]
  usuario_id bigint [not null]
  nome varchar(80) [not null]
  valor_meta numeric(14,2) [not null, note: 'RN11 - CHECK > 0']
  valor_atual numeric(14,2) [not null, default: 0, note: 'R07 - aporte manual no CP1']
  prazo date [null]
  criado_em timestamptz [not null, default: `now()`]
  atualizado_em timestamptz [not null, default: `now()`]

  Indexes {
    usuario_id
  }
}

Ref: conta.usuario_id > usuario.id [delete: cascade]
Ref: categoria.usuario_id > usuario.id [delete: cascade]
Ref: meta.usuario_id > usuario.id [delete: cascade]
Ref: transacao.conta_id > conta.id [delete: restrict]
Ref: transacao.categoria_id > categoria.id [delete: restrict]
```

---

## 8. Perguntas prováveis na apresentação

**"Por que a conta não guarda o saldo?"**
Porque saldo em coluna precisa ser atualizado em toda criação, edição e exclusão
de transação. Um caminho esquecido e o saldo diverge do extrato, sem erro nem
log. Calculado, é impossível divergir. RN07.

**"Por que a transação não tem `usuario_id`?"**
Porque o dono vem por `conta`. Repetir criaria dependência transitiva e violaria
a 3ª Forma Normal, além de permitir que a transação tivesse dois donos diferentes
dependendo de por onde se consulta.

**"Por que `categoria.usuario_id` aceita NULL?"**
NULL identifica categoria de sistema, compartilhada por todos. Evita que o
usuário recém-cadastrado precise criar categoria antes de lançar a primeira
despesa. RN16.

**"Por que NUMERIC e não FLOAT?"**
`0.1 + 0.2` não dá `0.3` em ponto flutuante. Em sistema financeiro isso vira
centavo perdido que não se consegue explicar. RN17.

**"Por que 404 e não 403 quando o recurso é de outro usuário?"**
403 confirma que o recurso existe e permite descobrir ids alheios por tentativa.
Para quem não é dono, o recurso não existe. RN01.
