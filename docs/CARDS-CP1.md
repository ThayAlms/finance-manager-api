# Cards do CP1 — CaixaLivre

14 cards para a lista **A fazer**. Cada card tem: membro atribuído (campo Membros,
não no título), descrição em Markdown e um ou mais checklists.

Recursos do Trello usados aqui:
- **Membros** no card — o responsável
- **Checklist** — sub-etapas; um card pode ter vários checklists nomeados
- **Item de checklist com responsável e prazo próprios** — usado no card do README
- **Etiquetas** — tipo de trabalho
- **Data de entrega** — prazo do card

## Distribuição

| Responsável | Cards | Prazo final |
|---|---|---|
| Vitor | 2, 3, 4, 5, 10, 11 | 07/09 |
| Thaina | 8, 9 | 06/09 |
| Silvio | 6, 7, 12 | 07/09 |
| Todos | 1, 13, 14 | 07/09 |

Thaina tem 2 cards mas são os dois maiores (Contas e Transações concentram quase
toda a regra de negócio). Vitor pega infraestrutura porque destrava os outros dois.

## Etiquetas a criar

| Cor | Nome |
|---|---|
| Verde | Backend / API |
| Azul | Banco de Dados |
| Laranja | Arquitetura / Setup |
| Amarelo | Documentação |
| Roxo | Apresentação |
| Vermelho | Bloqueador / Risco |

---

# 1. Modelagem do banco de dados (DER)

**Membros:** Vitor, Thaina, Silvio
**Etiqueta:** Banco de Dados · **Prazo:** 03/09

**Descrição:**

Definir o modelo de dados que sustenta todas as regras de negócio do CP1.
Nenhum CRUD começa antes deste card estar em Feito — os três dependem dele.

Entidades do CP1: `usuario`, `conta`, `categoria`, `transacao`, `meta`.

Decisões já fechadas (não reabrir sem discutir):
- Valores monetários em `NUMERIC(14,2)` → `Decimal`. Nunca `float`.
- `transacao` SEMPRE tem `conta_id`. Sem isso o saldo é impossível de calcular.
- `conta` guarda `saldo_inicial`; o saldo atual é **calculado**, não armazenado.
- `categoria.usuario_id` é anulável: NULL = categoria de sistema, preenchido = personalizada.
- Cartão de crédito não é modelado como conta — fica para o CP2.
- Toda entidade tem `criado_em` e `atualizado_em`.

Entregável: diagrama + descrição em `docs/modelo-dados.md`.

**Checklist — Modelagem**
- Listar entidades e atributos
- Definir tipos e enums (tipo, natureza)
- Definir chaves estrangeiras e cardinalidades
- Definir política de exclusão (RESTRICT em categoria e conta)
- Conferir se cada regra de negócio é representável no modelo
- Desenhar o DER (dbdiagram.io ou draw.io)
- Salvar diagrama e descrição em docs/

---

# 2. Setup do projeto e arquitetura

**Membros:** Vitor
**Etiqueta:** Arquitetura / Setup · **Prazo:** 03/09

**Descrição:**

Criar o repositório e a estrutura em camadas onde todo mundo vai trabalhar.
Precisa estar pronto antes de Thaina e Silvio começarem, senão eles ficam bloqueados.

Estrutura alvo:

```
app/
  main.py
  core/          config e seguranca
  models/        entidades SQLAlchemy
  schemas/       Pydantic (entrada e saida)
  repositories/  acesso ao banco
  services/      regras de negocio
  routers/       endpoints
```

A separação `models / schemas / services / routers` é o que vale os 3,0 pontos de
"arquitetura e organização do backend". Regra de negócio mora em `services`,
nunca dentro do router.

**Checklist — Setup**
- Criar repositório no GitHub e adicionar Thaina e Silvio
- .gitignore para Python (venv, __pycache__, .env)
- Criar a estrutura de pastas em camadas
- requirements.txt com as dependências
- FastAPI + Uvicorn subindo em localhost
- .env.example versionado (e .env fora do Git)
- Carregar configuração com Pydantic Settings
- README inicial e primeiro commit

---

# 3. Banco de dados: conexão e migrations

**Membros:** Vitor
**Etiqueta:** Banco de Dados · **Prazo:** 03/09

**Descrição:**

Conexão funcional com PostgreSQL e controle de versão do schema com Alembic.
O barema dá 3,0 pontos para "banco de dados e persistência" — o professor vai
querer ver as migrations e os dados persistindo de verdade, não um SQLite em memória.

**Checklist — Infra de banco**
- Subir o PostgreSQL (local ou Docker)
- Configurar engine e SessionLocal do SQLAlchemy
- Dependência get_db para injeção nas rotas
- Inicializar o Alembic
- Gerar e aplicar a migration inicial
- Testar leitura e escrita de ponta a ponta
- Script de seed com as categorias de sistema

---

# 4. Autenticação e usuários (JWT)

**Membros:** Vitor
**Etiqueta:** Backend / API · **Prazo:** 04/09

**Descrição:**

Cadastro, login e proteção de rotas. É o que sustenta a RN01 (cada usuário só
enxerga os próprios dados) — sem isso, nenhum outro CRUD consegue filtrar por dono.

Rotas: `POST /auth/registrar`, `POST /auth/login`, `GET /usuarios/me`, `PUT /usuarios/me`

Atenção: a senha nunca pode aparecer em nenhuma resposta da API. Guardar apenas
o hash, em campo `senha_hash`.

**Checklist — Implementação**
- Entidade Usuario com e-mail único
- Hash de senha com bcrypt (passlib)
- POST /auth/registrar
- POST /auth/login devolvendo o JWT
- Dependência get_usuario_atual lendo o token
- Aplicar a dependência em todas as rotas protegidas
- GET e PUT /usuarios/me

**Checklist — Regras de negócio**
- RN01 — usuário só acessa os próprios dados
- RN02 — e-mail único (409 se duplicado)
- RN03 — senha só como hash e nunca retornada
- Token ausente ou inválido devolve 401

---

# 5. Padrão de respostas e tratamento de erros

**Membros:** Vitor
**Etiqueta:** Arquitetura / Setup · **Prazo:** 04/09

**Descrição:**

Handler global de exceções e um formato único de erro para toda a API. O enunciado
pede explicitamente "respostas padronizadas", "códigos HTTP coerentes" e
"tratamento básico de erros" — três exigências resolvidas num card só.

Formato de erro da API:

```json
{
  "erro": "RECURSO_NAO_ENCONTRADO",
  "mensagem": "Conta não encontrada.",
  "detalhes": null
}
```

**Checklist — Implementação**
- Exceções de domínio próprias (NaoEncontrado, Conflito, NaoAutorizado)
- Handler global registrado no FastAPI
- Formato único de resposta de erro
- Tradução do erro de validação do Pydantic (422)
- Testar 400, 401, 403, 404, 409 e 422

**Checklist — Códigos por operação**
- GET lista → 200
- GET por id inexistente → 404
- POST criado → 201
- POST inválido → 422
- DELETE com vínculo → 409
- DELETE com sucesso → 204

---

# 6. CRUD de Categorias

**Membros:** Silvio
**Etiqueta:** Backend / API · **Prazo:** 05/09

**Descrição:**

CRUD completo de `/categorias`, cobrindo as categorias de sistema (já vêm
cadastradas, iguais para todos) e as personalizadas de cada usuário.

Como diferenciar: `categoria.usuario_id` NULL = de sistema; preenchido = do usuário.
A listagem devolve as duas juntas.

Depende de: cards 2, 3 e 4 em Feito.

**Checklist — Endpoints**
- GET /categorias (sistema + do usuário)
- GET /categorias/{id}
- POST /categorias
- PUT /categorias/{id}
- DELETE /categorias/{id}

**Checklist — Regras de negócio**
- RN08 — categoria com transação vinculada não pode ser excluída (409)
- RN09 — categoria de sistema não pode ser editada nem excluída (403)
- Nome único por usuário e tipo (409 se repetir)
- Usuário não enxerga categoria personalizada de outro usuário

**Checklist — Definition of Done**
- Códigos HTTP corretos em todos os casos
- Aparece no Swagger com exemplos
- Testado manualmente na coleção de requisições
- Revisado por Vitor ou Thaina

---

# 7. CRUD de Metas

**Membros:** Silvio
**Etiqueta:** Backend / API · **Prazo:** 05/09

**Descrição:**

CRUD de `/metas` mais o cálculo de progresso. Meta é o objetivo de economia do
usuário — por exemplo "Reserva de emergência — R$ 5.000".

Decisão: no CP1 o `valor_atual` é atualizado manualmente (aporte do usuário).
Derivar automaticamente das transações fica para o CP2. Registrado aqui para não
virar discussão no meio do desenvolvimento.

**Checklist — Endpoints**
- GET /metas
- GET /metas/{id} com progresso
- POST /metas
- PUT /metas/{id}
- DELETE /metas/{id}

**Checklist — Regras de negócio**
- RN11 — valor_meta deve ser maior que zero
- RN11 — progresso = valor_atual / valor_meta, em %
- RN11 — devolver também quanto falta para atingir
- RN12 — marcar meta como atingida quando valor_atual >= valor_meta
- Usuário só acessa as próprias metas

**Checklist — Definition of Done**
- Códigos HTTP corretos em todos os casos
- Aparece no Swagger com exemplos
- Testado manualmente na coleção de requisições
- Revisado por Vitor ou Thaina

---

# 8. CRUD de Contas

**Membros:** Thaina
**Etiqueta:** Backend / API · **Prazo:** 05/09

**Descrição:**

CRUD de `/contas` e o cálculo de saldo. Conta é onde o dinheiro está:
conta corrente, poupança ou carteira.

Decisão importante: **saldo não é coluna**. A conta guarda `saldo_inicial` e o
saldo atual é calculado como `saldo_inicial + soma(receitas) - soma(despesas)`.
Isso evita o clássico saldo divergente e é um bom ponto para defender na apresentação.

O campo `natureza` (PESSOAL ou NEGOCIO) é o que separa o dinheiro pessoal do
dinheiro do negócio — é o diferencial do nosso recorte de autônomos e MEIs.

Depende de: cards 2, 3 e 4 em Feito.

**Checklist — Endpoints**
- GET /contas com saldo calculado
- GET /contas/{id}
- POST /contas
- PUT /contas/{id}
- DELETE /contas/{id}

**Checklist — Regras de negócio**
- RN07 — saldo = saldo_inicial + receitas − despesas
- RN10 — conta com transação vinculada não pode ser excluída (409)
- RN14 — natureza PESSOAL ou NEGOCIO obrigatória
- Usuário só acessa as próprias contas

**Checklist — Definition of Done**
- Códigos HTTP corretos em todos os casos
- Aparece no Swagger com exemplos
- Testado manualmente na coleção de requisições
- Revisado por Vitor

---

# 9. CRUD de Transações

**Membros:** Thaina
**Etiqueta:** Backend / API · **Prazo:** 06/09

**Descrição:**

O coração da API. Transação é cada entrada ou saída de dinheiro, sempre ligada a
uma conta e a uma categoria.

É o card com mais regra de negócio do CP1 e o que o professor mais vai testar na
demonstração. A listagem com filtros também cobre o requisito de "Histórico"
do escopo.

Depende de: cards 6 e 8 em Feito.

**Checklist — Endpoints**
- GET /transacoes com filtros e paginação
- GET /transacoes/{id}
- POST /transacoes
- PUT /transacoes/{id}
- DELETE /transacoes/{id}

**Checklist — Filtros da listagem**
- Por período (data_inicio e data_fim)
- Por tipo (RECEITA ou DESPESA)
- Por categoria
- Por conta
- Por natureza (PESSOAL ou NEGOCIO)
- Paginação e ordenação por data

**Checklist — Regras de negócio**
- RN04 — valor deve ser maior que zero
- RN05 — tipo da transação deve bater com o tipo da categoria
- RN06 — conta e categoria devem pertencer ao usuário autenticado
- RN13 — data não pode ser futura no CP1
- Usuário só acessa as próprias transações

**Checklist — Definition of Done**
- Códigos HTTP corretos em todos os casos
- Aparece no Swagger com exemplos
- Testado manualmente na coleção de requisições
- Revisado por Vitor

---

# 10. Endpoint de resumo financeiro

**Membros:** Vitor
**Etiqueta:** Backend / API · **Prazo:** 06/09

**Descrição:**

`GET /resumo` — um único endpoint que devolve a visão do mês. É o card de maior
retorno na apresentação: mostra regra de negócio funcionando em vez de mais um
CRUD, e já prepara o dashboard do CP2.

Retorno esperado:

```json
{
  "saldo_total": 4820.50,
  "receitas_mes": 7200.00,
  "despesas_mes": 3150.00,
  "economia_mes": 4050.00,
  "por_natureza": { "pessoal": 1800.00, "negocio": 3020.00 }
}
```

Depende de: cards 8 e 9 em Feito.

**Checklist — Cálculos**
- Saldo total somando todas as contas do usuário
- Receitas do mês corrente
- Despesas do mês corrente
- Economia do mês (receitas − despesas)
- Separação por natureza (pessoal x negócio)
- Aceitar mês e ano por query param (default: mês atual)

---

# 11. Documentação Swagger/OpenAPI

**Membros:** Vitor
**Etiqueta:** Documentação · **Prazo:** 07/09

**Descrição:**

Vale 2,0 pontos e o FastAPI entrega a maior parte de graça. O trabalho aqui é
deixar navegável: o professor precisa abrir `/docs`, entender a API e conseguir
testar sem perguntar nada para o grupo.

Fazer só depois que os CRUDs estiverem em Feito.

**Checklist — Documentação**
- Título, descrição e versão da API
- Agrupar endpoints por tag (Auth, Contas, Categorias, Transações, Metas, Resumo)
- Descrição em cada endpoint
- Exemplos de request e response nos schemas
- Documentar os códigos de erro possíveis
- Botão "Authorize" funcionando com o JWT
- Testar a API inteira pelo próprio Swagger

---

# 12. README do projeto

**Membros:** Silvio (dono), Thaina, Vitor
**Etiqueta:** Documentação · **Prazo:** 07/09

**Descrição:**

Vale 2,0 pontos e o enunciado lista exatamente o que precisa ter. Dá para dividir
entre os três: no Trello, clique em cada item do checklist e use **Atribuir** para
marcar o responsável daquele item específico.

**Checklist — Conteúdo** (atribuir item por item)
- Nome do projeto e descrição — Silvio
- Problema escolhido e solução proposta — Silvio
- Integrantes do grupo — Silvio
- Tecnologias utilizadas — Silvio
- Arquitetura inicial — Vitor
- Instruções de instalação — Vitor
- Configuração das variáveis de ambiente — Vitor
- Instruções para execução — Vitor
- Banco de dados utilizado — Thaina
- Principais endpoints — Thaina
- Link da documentação Swagger — Thaina
- Link do Trello — Thaina

---

# 13. Revisão final e entrega

**Membros:** Vitor, Thaina, Silvio
**Etiqueta:** Bloqueador / Risco · **Prazo:** 07/09

**Descrição:**

Subir o projeto do zero, em pasta limpa, seguindo apenas o que está escrito no
README. Se não subir, o README está errado — e é exatamente isso que o professor
vai fazer.

**Checklist — Teste do zero**
- Clonar o repositório em pasta limpa
- Seguir o README sem nenhum passo extra
- Banco criado e migrations aplicadas
- Coleção de requisições (Insomnia ou Postman) versionada no repo
- Testar todos os endpoints pela coleção
- Conferir os códigos HTTP de erro
- Swagger abrindo e funcional

**Checklist — Entregáveis do CP1**
- Link do repositório GitHub
- README completo
- Código-fonte do backend
- Banco de dados configurado
- API funcional
- Documentação Swagger
- Link do Trello
- Apresentação pronta

---

# 14. Apresentação do CP1

**Membros:** Vitor, Thaina, Silvio
**Etiqueta:** Apresentação · **Prazo:** 07/09

**Descrição:**

O enunciado diz que "todos os integrantes deverão estar preparados para explicar
partes técnicas", e isso vale 2,0 pontos. Cada um apresenta o que construiu —
ninguém apresenta a parte do outro.

Divisão:
- **Vitor** — arquitetura, autenticação e endpoint de resumo
- **Thaina** — contas, transações e a regra de saldo derivado
- **Silvio** — categorias, metas e modelo de dados

**Checklist — Roteiro**
- Problema escolhido e público-alvo
- Proposta de solução e escopo do CP1
- Regras de negócio principais
- Arquitetura e organização do projeto
- Modelo de dados e relacionamentos
- Demonstração ao vivo no Swagger
- Organização do time no Trello
- Roadmap do CP2 e CP3

**Checklist — Preparação**
- Cada um ensaia a própria parte
- Ensaio completo cronometrado
- Dados de exemplo cadastrados para a demo
- Plano B caso a internet ou o banco falhem
