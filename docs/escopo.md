# Escopo — CaixaLivre (CP1)

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

## Escopo do CP1

- Backend em FastAPI + PostgreSQL (SQLAlchemy 2 + Alembic para migrations).
- Autenticação e autorização via JWT.
- CRUD completo de conta, categoria, transação e meta.
- Endpoint de resumo financeiro (`/resumo`).
- Documentação interativa via Swagger/OpenAPI.

## Fora do escopo do CP1

Cartão de crédito, transferência entre contas, recorrência/parcelamento,
recuperação de senha, notificações, exportação e frontend ficam para o CP2 ou
CP3 — motivo de cada adiamento na tabela **Restrições relevantes** de
[regras-de-negocio.md](regras-de-negocio.md).

## Integrantes

Vitor Barbosa Vitorino, Thainá Almeida Santos, Silvio Dela Libera Neto.
