# Quadro Trello — CaixaLivre (CP1 → CP3)

> Quadro único para todo o projeto. As **listas** carregam o fluxo de trabalho;
> as **etiquetas** carregam a etapa (CP1/CP2/CP3) e o tipo de trabalho.
>
> Truque de montagem: em **Adicionar um cartão**, cole o bloco inteiro (várias
> linhas) → o Trello pergunta *"Deseja adicionar N cartões?"* → confirme.

## Dados do quadro

- **Nome:** `CaixaLivre — Controle Financeiro`
- **Visibilidade:** Público (o professor precisa abrir o link sem convite)
- **Membros:** Vitor, Thaina, Silvio

**Descrição do quadro** (colar em Menu → Sobre este quadro → Editar):

```
Gestao financeira para autonomos, freelancers e MEIs.
Backend em Python + FastAPI + PostgreSQL.

Etapas:
CP1 (08/09) - backend, API REST, banco e Swagger
CP2 (06/10) - frontend, dashboard, LLM e testes iniciais
CP3 (27/10) - testes, deploy, containerizacao e monetizacao

Integrantes: Vitor, Thaina, Silvio
Repositorio: <link>
Swagger: <link>
Documentacao de escopo, regras de negocio e DER: /docs no repositorio
```

Prefixos nos títulos: `[V]` Vitor · `[T]` Thaina · `[S]` Silvio · `[TODOS]` o time.

---

## Listas (apenas estas quatro)

| # | Lista | Regra de entrada |
|---|---|---|
| 1 | `📥 A Fazer` | Backlog priorizado. O topo é o que vem a seguir. |
| 2 | `🔧 Fazendo` | **Máx. 2 cartões por pessoa.** Só entra com responsável definido. |
| 3 | `👀 Review` | Só entra com o checklist *Definition of Done* concluído. |
| 4 | `✅ Feito` | Só entra depois de revisado por **outro** integrante. |

Duas regras que valem os pontos de metodologia ágil e que resolvem problema real
do time (o Silvio nunca fica travado sozinho, e nada chega no dia 08 sem
segunda leitura):

- **Limite de WIP em `Fazendo`:** no máximo 2 cartões por pessoa. Se você quer
  puxar um terceiro, primeiro destrava o que está parado.
- **Review cruzado:** quem escreveu não move para `Feito`. Vitor revisa Thaina e
  Silvio; Thaina revisa Vitor.

> A documentação viva (DER, regras de negócio, decisões técnicas) mora no `/docs`
> do repositório, **não** em cartão. Cartão de documentação é a *tarefa de
> escrever*; ela flui e termina em `Feito` como qualquer outra.

---

## Etiquetas

**Etapa** — é o que substitui as listas por sprint:

| Cor | Nome |
|---|---|
| Verde | `CP1 — Backend & API` |
| Amarelo | `CP2 — Frontend & IA` |
| Vermelho | `CP3 — Testes & Deploy` |

**Tipo de trabalho** — permite filtrar por quem faz o quê:

| Cor | Nome |
|---|---|
| Azul | `Banco de Dados` |
| Roxo | `Arquitetura / Setup` |
| Azul-céu | `Documentação` |
| Rosa | `Apresentação` |
| Preto | `Bloqueador / Risco` |

Com isso, o filtro `CP1` mostra a sprint atual sem esconder o resto do projeto —
e no CP2 basta trocar o filtro, sem remodelar nada.

---

## Atalhos que economizam tempo na montagem

Passe o mouse sobre um cartão (sem abrir) e:

| Tecla | Ação |
|---|---|
| `1` … `9` | Aplica/remove a etiqueta correspondente |
| `d` | Abre a data de entrega |
| `espaço` | Atribui você mesmo ao cartão |
| `l` | Abre o menu de etiquetas |

Depois de colar os blocos, etiquetar os 52 cartões leva ~2 minutos com as teclas
numéricas.

---

## Bloco 1 → colar em `📥 A Fazer` (cartões do CP1, em ordem de execução)

```
[TODOS] Fechar modelo de dados (DER) e regras de negócio
[V] Criar repositório GitHub, .gitignore e estrutura de pastas
[V] Configurar FastAPI + Uvicorn com separação em camadas
[V] Configurar PostgreSQL + SQLAlchemy + Alembic
[V] Criar .env.example e carregar config via Pydantic Settings
[V] Handler global de erros e formato padrão de resposta
[V] Configurar Swagger: metadados, tags, exemplos e botão de auth
[V] Entidade Usuario + hash de senha com bcrypt
[V] POST /auth/registrar e POST /auth/login com JWT
[V] Dependência get_usuario_atual e proteção das rotas
[S] Entidade Categoria + seed das categorias de sistema
[S] CRUD completo de /categorias
[S] Regra: bloquear exclusão de categoria com transações (409)
[T] Entidade Conta + migration
[T] CRUD completo de /contas
[T] Regra: saldo da conta derivado das transações
[T] Entidade Transacao + relacionamentos com Conta e Categoria
[T] CRUD completo de /transacoes
[T] GET /transacoes com filtros de período, tipo, categoria e conta
[T] Validações da transação: valor > 0, tipo x categoria, conta do usuário
[S] Entidade Meta + migration
[S] CRUD completo de /metas
[S] GET /metas/{id} com progresso em % e valor restante
[V] GET /resumo: saldo, receitas do mês, despesas do mês e economia
[TODOS] Documento de escopo e regras de negócio em docs/
[S] README: nome, descrição, problema, solução e integrantes
[V] README: arquitetura, instalação, variáveis de ambiente e execução
[T] README: endpoints principais, banco e links do Swagger e Trello
[V] Coleção de requisições para a demo (Insomnia/Postman/.http)
[TODOS] Revisão final: subir do zero e testar todos os endpoints
[TODOS] Ensaio da apresentação — cada um explica a sua parte
```

→ Selecionar todos e aplicar a etiqueta verde `CP1 — Backend & API`.

## Bloco 2 → colar em `📥 A Fazer`, abaixo do bloco 1

```
[CP2] Frontend do app: telas e navegação
[CP2] Dashboard com gráficos de pizza, barras e linhas
[CP2] Cartão de crédito: limite, fatura, fechamento e vencimento
[CP2] Parcelamento de compras
[CP2] Transações recorrentes: aluguel, internet, assinaturas
[CP2] Contas a pagar e a receber
[CP2] Transferência entre contas
[CP2] Classificação automática de categoria com LLM
[CP2] Chatbot financeiro com perguntas em linguagem natural
[CP2] Previsão de saldo e de gastos futuros
[CP2] Detecção de gastos incomuns
[CP2] Normalização e otimização do banco
[CP2] Testes iniciais: unitários e de integração
[CP2] Ajuste da documentação Swagger
[CP2] Otimização da API
```

→ Etiqueta amarela `CP2 — Frontend & IA`.

## Bloco 3 → colar em `📥 A Fazer`, abaixo do bloco 2

```
[CP3] Suíte de testes completa
[CP3] Containerização com Docker e docker-compose
[CP3] Deploy em nuvem
[CP3] Notificações e lembretes de vencimento
[CP3] Exportação para PDF e Excel
[CP3] Recuperação de senha por e-mail
[CP3] Modelo de monetização
[CP3] Teste com usuário real
```

→ Etiqueta vermelha `CP3 — Testes & Deploy`.

Total: **54 cartões**, todos em `A Fazer`. `Fazendo`, `Review` e `Feito`
começam vazias — é o estado correto de um quadro no dia 1.

---

## Prazos (campo Data de Entrega, só nos cartões do CP1)

| Cartões | Prazo |
|---|---|
| Modelagem, setup, camadas, banco, erros e Swagger | **03/09** (qui) |
| Auth, JWT e proteção de rotas | **04/09** (sex) |
| CRUDs de Categoria, Conta e Meta | **05/09** (sáb) |
| Transação, filtros, validações e `/resumo` | **06/09** (dom) |
| Escopo, README, coleção da demo e ensaio | **07/09** (seg, feriado) |
| **Entrega** | **08/09** (ter) |

Nos cartões de CP2 e CP3, deixe sem data por enquanto — data em cartão que
ninguém vai cumprir só polui o quadro com vermelho.

---

## Checklists a criar dentro dos cartões

### Definition of Done — usar em **todo** cartão de código

```
Endpoint responde com o código HTTP correto
Erros tratados e no formato padrão
Aparece corretamente no Swagger
Regra de negócio validada
Testado manualmente na coleção de requisições
Revisado por outro integrante
```

### Entregáveis do CP1 — no cartão `[TODOS] Revisão final`

```
Link do repositório GitHub
README atualizado e completo
Código-fonte do backend
Banco de dados configurado e com migrations
API funcional com todos os CRUDs
Documentação Swagger acessível
Link do Trello
Apresentação preparada
```

---

# Referência técnica (vai para `/docs` no repositório, não para o Trello)

## Decisões técnicas

```
Stack: Python 3.12 + FastAPI + SQLAlchemy 2 + Alembic + PostgreSQL
Auth: JWT (python-jose) com senha em bcrypt (passlib)
Validacao: Pydantic v2
Docs: Swagger/OpenAPI nativo do FastAPI em /docs

Decisoes tomadas:
- Valores monetarios em Numeric(14,2) -> Decimal. Nunca float.
- Saldo da conta NAO e coluna mutavel. Conta guarda saldo_inicial;
  o saldo atual e calculado: saldo_inicial + soma(receitas) - soma(despesas).
- Categoria tem usuario_id anulavel: NULL = categoria de sistema,
  preenchido = categoria personalizada do usuario.
- Transacao SEMPRE tem conta_id. Sem isso o saldo e impossivel de calcular.
- Cartao de credito NAO e modelado como Conta. Fica para o CP2.
- Transferencia entre contas: fora do escopo do CP1.
- Toda entidade tem criado_em e atualizado_em.
- Exclusao de categoria com transacoes vinculadas: RESTRICT (HTTP 409).
```

## Regras de negócio

```
RN01 - Todo usuario so enxerga e manipula os proprios dados.
RN02 - Email do usuario e unico no sistema.
RN03 - Senha e armazenada apenas como hash e nunca retorna na API.
RN04 - Valor de transacao deve ser maior que zero.
RN05 - O tipo da transacao (RECEITA/DESPESA) deve ser igual ao tipo da categoria.
RN06 - Conta e categoria da transacao devem pertencer ao usuario autenticado
       (ou ser categoria de sistema).
RN07 - Saldo da conta = saldo_inicial + soma(receitas) - soma(despesas).
RN08 - Categoria com transacoes vinculadas nao pode ser excluida (409).
RN09 - Categoria de sistema nao pode ser editada nem excluida pelo usuario.
RN10 - Conta com transacoes nao pode ser excluida (409).
RN11 - Meta tem valor_meta > 0; o progresso e valor_atual / valor_meta.
RN12 - Meta atingida quando valor_atual >= valor_meta.
RN13 - Data da transacao nao pode ser futura no CP1 (lancamentos futuros = CP2).
RN14 - Conta e transacao tem natureza PESSOAL ou NEGOCIO, para separar
       o dinheiro do autonomo do dinheiro da pessoa fisica.
```

## Modelo de dados (DER)

```
usuario (id, nome, email UNIQUE, senha_hash, criado_em, atualizado_em)

conta (id, usuario_id FK, nome, tipo ENUM[CORRENTE|POUPANCA|CARTEIRA],
       natureza ENUM[PESSOAL|NEGOCIO], saldo_inicial NUMERIC(14,2),
       criado_em, atualizado_em)

categoria (id, usuario_id FK NULLABLE, nome, tipo ENUM[RECEITA|DESPESA],
           criado_em, atualizado_em)
           UNIQUE (usuario_id, nome, tipo)

transacao (id, usuario_id FK, conta_id FK, categoria_id FK,
           descricao, valor NUMERIC(14,2), data DATE,
           tipo ENUM[RECEITA|DESPESA],
           natureza ENUM[PESSOAL|NEGOCIO], criado_em, atualizado_em)

meta (id, usuario_id FK, nome, valor_meta NUMERIC(14,2),
      valor_atual NUMERIC(14,2), prazo DATE NULLABLE,
      criado_em, atualizado_em)

Cardinalidades:
usuario 1--N conta | 1--N categoria | 1--N transacao | 1--N meta
conta     1--N transacao
categoria 1--N transacao
```

## Endpoints do CP1

| Método | Rota | Descrição |
|---|---|---|
| POST | `/auth/registrar` | Cria usuário |
| POST | `/auth/login` | Retorna JWT |
| GET | `/usuarios/me` | Perfil do usuário logado |
| PUT | `/usuarios/me` | Atualiza perfil |
| GET/POST | `/contas` | Lista / cria conta |
| GET/PUT/DELETE | `/contas/{id}` | Detalha / atualiza / exclui |
| GET/POST | `/categorias` | Lista / cria categoria |
| GET/PUT/DELETE | `/categorias/{id}` | Detalha / atualiza / exclui |
| GET/POST | `/transacoes` | Lista com filtros / cria |
| GET/PUT/DELETE | `/transacoes/{id}` | Detalha / atualiza / exclui |
| GET/POST | `/metas` | Lista / cria meta |
| GET/PUT/DELETE | `/metas/{id}` | Detalha / atualiza / exclui |
| GET | `/resumo` | Saldo, receitas, despesas e economia do mês |

Total: **13 rotas / 5 entidades**.
