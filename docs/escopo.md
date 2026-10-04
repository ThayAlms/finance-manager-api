# Escopo — CaixaLivre

## Problema

Autônomos, freelancers e MEIs costumam misturar o dinheiro pessoal com o do
negócio na mesma conta e no mesmo controle (ou na ausência de um). Isso torna
difícil responder perguntas básicas: quanto sobrou do mês, quanto é receita do
negócio, quanto já foi poupado para uma meta.

## Público-alvo

Autônomos, freelancers e microempreendedores individuais (MEIs) que precisam
de controle financeiro simples, mas com separação clara entre finanças
pessoais e finanças do negócio.

## Solução proposta

CaixaLivre é uma API REST de gestão financeira que permite ao usuário:

- Cadastrar contas (corrente, poupança, carteira) com saldo calculado a partir
  do histórico de transações — nunca um valor solto que pode divergir.
- Classificar receitas e despesas por categoria, com categorias padrão do
  sistema e categorias personalizadas por usuário.
- Registrar transações associadas a conta e categoria, com filtros por
  período, tipo e natureza.
- Marcar toda conta e transação como **PESSOAL** ou **NEGÓCIO** — o
  diferencial do produto para o público de autônomos e MEIs.
- Definir metas de economia e acompanhar o progresso.
- Consultar um resumo financeiro do mês (saldo, receitas, despesas, economia).

Detalhamento de cada regra em [regras-de-negocio.md](regras-de-negocio.md) e o
modelo de dados completo em [modelo-dados.md](modelo-dados.md).

## Entidades e relacionamentos

Cinco entidades:

| Entidade | O que representa |
|---|---|
| `usuario` | Quem usa o sistema: nome, e-mail de login e senha em hash. É o dono de tudo. |
| `conta` | Onde o dinheiro fica — corrente, poupança ou carteira — com natureza PESSOAL ou NEGOCIO e um saldo inicial. |
| `categoria` | Classificação de receita ou de despesa. Pode ser de sistema (vale para todos) ou personalizada do usuário. |
| `transacao` | O lançamento: uma receita ou despesa em uma conta, classificada por uma categoria, com data, valor e natureza. |
| `meta` | Objetivo de economia do usuário: valor alvo, valor já guardado e prazo opcional. |

Cardinalidades:

- `usuario` **1 : N** `conta` — o usuário tem quantas contas quiser, e toda
  conta tem exatamente um dono.
- `usuario` **1 : N** `categoria` — vale para as personalizadas. As de sistema
  não têm dono e são compartilhadas por todos os usuários.
- `usuario` **1 : N** `meta`.
- `conta` **1 : N** `transacao` — toda transação sai de uma conta. É esse
  vínculo que permite calcular o saldo.
- `categoria` **1 : N** `transacao` — toda transação é classificada por
  exatamente uma categoria.

`transacao` não guarda `usuario_id`: o dono é alcançado por
`transacao → conta → usuario`. Repetir o campo criaria dependência transitiva
(violação da 3ª Forma Normal) e permitiria que a mesma transação tivesse dois
donos diferentes dependendo de por onde fosse consultada.

Diagrama em [der.png](der.png). Colunas, tipos, constraints e índices em
[modelo-dados.md](modelo-dados.md).

## Escopo da primeira versão

- Backend em FastAPI + PostgreSQL (SQLAlchemy 2 + Alembic para migrations).
- Autenticação e autorização via JWT.
- CRUD completo de conta, categoria, transação e meta.
- Endpoint de resumo financeiro (`/resumo`) e insights educativos (`/insights`).
- Documentação interativa via Swagger/OpenAPI.
- Frontend web responsivo com dashboard de controle.
- Importação assistida de extratos PDF/CSV/OFX, com revisão antes da persistência.

## Fora do escopo

Cartão de crédito, transferência entre contas, recorrência/parcelamento,
recuperação de senha, notificações e exportação ficam para versões
seguintes — o motivo de cada adiamento está na tabela **Restrições relevantes**
de [regras-de-negocio.md](regras-de-negocio.md).

## Integrantes

Vitor Barbosa Vitorino, Thainá Almeida Santos, Silvio Dela Libera Neto.
