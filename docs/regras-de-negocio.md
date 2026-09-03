# Regras de negócio — CaixaLivre (CP1)

Documento de referência do grupo. Alimenta o card 15 do Trello, o `docs/escopo.md`,
a seção de regras do README e o roteiro da apresentação.

Cada regra tem: o enunciado, **por que existe**, onde é aplicada no código e o que
a API responde quando é violada. Regra sem justificativa é decoração — na
apresentação o professor vai perguntar "por quê", e a resposta precisa estar aqui.

**Numeração:** RN01 a RN14 são as já referenciadas nos checklists dos cards do
Trello — não renumerar. RN15 a RN17 são acréscimos deste documento.

---

## A. Acesso e identidade

### RN01 — Isolamento de dados por usuário

Toda conta, categoria personalizada, transação e meta pertence a exatamente um
usuário. Nenhuma leitura, alteração ou exclusão pode alcançar dado de outro usuário.

**Por quê:** é o que faz a aplicação ser multiusuário de verdade. Sem isso, dois
usuários de teste enxergam o mesmo saldo e a demonstração desmonta na hora.

**Onde:** toda query filtra por `usuario_id` extraído do JWT — **nunca** de um
parâmetro vindo da requisição.

**Violação:** `404 Not Found`, não `403`. Devolver 403 confirma que o recurso
existe e permite descobrir ids de outros usuários por tentativa. Para quem não é
dono, o recurso simplesmente não existe.

### RN02 — E-mail único

Não podem existir dois usuários com o mesmo e-mail. Vale no cadastro e na
alteração de perfil.

**Onde:** constraint `UNIQUE` no banco (a garantia real) mais verificação no
service (para devolver mensagem legível em vez do erro cru do Postgres).

**Violação:** `409 Conflict`.

### RN03 — Senha nunca é armazenada nem devolvida em texto

Guardar apenas o hash bcrypt, em campo `senha_hash`. Nenhum schema de resposta
da API pode conter o campo senha, em nenhuma forma.

**Onde:** hash no service de usuário; o schema Pydantic de saída simplesmente
não declara o campo — assim é impossível vazar por esquecimento.

**Violação:** é erro de implementação, não de runtime. Vira item obrigatório no
checklist de review do card de autenticação.

---

## B. Transações

### RN04 — Valor sempre positivo

`valor > 0` em qualquer transação. O sinal do dinheiro vem do **tipo**
(RECEITA soma, DESPESA subtrai), nunca do valor.

**Por quê:** guardar despesa como número negativo parece prático e destrói os
relatórios — toda soma passa a precisar de tratamento especial, e um erro de
sinal vira saldo errado silencioso, sem exceção nem log.

**Violação:** `422 Unprocessable Entity`.

### RN05 — Coerência entre tipo da transação e tipo da categoria

Transação do tipo DESPESA só aceita categoria do tipo DESPESA. Idem para RECEITA.

**Por quê:** sem essa regra dá para lançar "Salário" como despesa, e o relatório
por categoria vira lixo. É a regra que o professor tem mais chance de tentar
quebrar na demonstração — vale deixar pronta uma requisição que mostra o 422.

**Onde:** service de transação, antes de persistir.

**Violação:** `422`.

### RN06 — Posse dos vínculos

A conta e a categoria informadas na transação devem pertencer ao usuário
autenticado. Exceção: categoria de sistema, que é de todos (ver RN16).

**Por quê:** sem essa checagem, um usuário lança transação na conta de outro
apenas passando o id na mão. É o furo mais comum em CRUD de faculdade.

**Violação:** `404` para o id que não é dele — mesmo raciocínio da RN01.

### RN13 — Sem lançamento futuro no CP1

A `data` da transação não pode ser maior que a data de hoje.

**Por quê:** transação com data futura é "conta a pagar", que é outro conceito,
com regra própria (previsto x realizado) e está planejado para o CP2. Aceitar
data futura agora quebraria o `/resumo`, que passaria a somar dinheiro que ainda
não entrou.

**Violação:** `422`.

---

## C. Contas e saldo

### RN07 — Saldo é calculado, nunca armazenado

```
saldo_atual = saldo_inicial + Σ(transações RECEITA) − Σ(transações DESPESA)
```
considerando apenas as transações daquela conta.

**Por quê:** saldo guardado em coluna precisa ser atualizado na criação, na
edição e na exclusão de transação — e também quando a transação muda de conta.
Basta um caminho esquecido para o saldo divergir do extrato, e aí não há como
saber qual dos dois está certo. Calculado, é impossível divergir.

**Custo aceito:** uma agregação por consulta. No volume do CP1 é irrelevante.
Se virar gargalo no CP3, a solução é cache — não voltar a coluna mutável.

**Onde:** repository/service de conta.

### RN10 — Conta com transação não pode ser excluída

**Por quê:** exclusão em cascata apagaria o histórico financeiro do usuário sem
aviso. O correto é bloquear e exigir que ele mova ou apague as transações antes.

**Onde:** verificação no service mais FK com `ON DELETE RESTRICT` no banco.

**Violação:** `409`, com mensagem informando quantas transações estão vinculadas.

### RN14 — Natureza obrigatória (PESSOAL ou NEGOCIO)

Toda conta e toda transação carrega `natureza` = PESSOAL ou NEGOCIO.

**Por quê:** é o núcleo do nosso recorte. A dor específica do autônomo e do MEI
é não conseguir separar o dinheiro da pessoa do dinheiro do negócio. Sem esse
campo, o produto vira mais um controle financeiro genérico e o recorte de
público-alvo deixa de se sustentar.

**Regra derivada:** a transação herda a natureza da conta por padrão, mas pode
ser sobrescrita — o autônomo frequentemente paga uma despesa do negócio pela
conta pessoal.

**Violação:** `422`.

---

## D. Categorias

### RN08 — Categoria com transação não pode ser excluída

**Por quê:** mesma lógica da RN10. Apagar em cascata apagaria transações; o
correto é o usuário reclassificar antes.

**Onde:** service mais `ON DELETE RESTRICT`.

**Violação:** `409`, informando quantas transações usam a categoria.

### RN09 — Categoria de sistema é imutável pela API

Categorias com `usuario_id` NULL não podem ser editadas nem excluídas por
nenhum usuário.

**Violação:** `403 Forbidden`. Aqui o 403 é correto — o recurso é público e o
usuário sabe que ele existe; o que falta é permissão.

### RN15 — Nome de categoria único por usuário e tipo

Um usuário não pode ter duas categorias de despesa chamadas "Transporte". Pode
ter uma de despesa e uma de receita com o mesmo nome.

**Onde:** `UNIQUE (usuario_id, nome, tipo)`.

**Violação:** `409`.

### RN16 — Categorias de sistema são compartilhadas

Existe um conjunto padrão criado no seed, com `usuario_id` NULL, visível para
todos. A listagem devolve as de sistema mais as personalizadas do usuário.

**Por quê:** usuário recém-cadastrado precisa conseguir lançar a primeira
despesa sem antes ter que cadastrar categoria. Reduz o atrito do primeiro uso e
evita banco vazio na demonstração.

---

## E. Metas

### RN11 — Meta válida e cálculo de progresso

`valor_meta > 0`.

```
progresso_percentual = min(100, valor_atual / valor_meta × 100)
valor_restante       = max(0, valor_meta − valor_atual)
```

**Onde:** calculado na leitura, não armazenado — mesmo princípio da RN07.

**Violação de `valor_meta <= 0`:** `422`.

### RN12 — Meta atingida

`atingida = valor_atual >= valor_meta`. Campo booleano calculado, devolvido na
resposta.

---

## F. Valores monetários

### RN17 — Moeda e precisão

Todos os valores em reais (BRL), `NUMERIC(14,2)` no banco e `Decimal` na
aplicação. **Proibido usar float.**

**Por quê:** em ponto flutuante, `0.1 + 0.2` não dá `0.3`. Em sistema
financeiro isso vira centavo perdido que ninguém consegue explicar e que só
aparece depois de muitas transações.

---

## Restrições relevantes do CP1

O enunciado pede "restrições relevantes" como item separado das regras de
negócio. Declarar limite é decisão de escopo, e decisão de escopo pontua.

| # | Restrição | Motivo | Vai para |
|---|---|---|---|
| R01 | Sem multi-moeda — apenas BRL | Conversão exige cotação e histórico de câmbio | — |
| R02 | Sem transferência entre contas | Não é receita nem despesa; exige saída e entrada atômicas com regra própria | CP2 |
| R03 | Cartão de crédito não é modelado | Fatura, limite, fechamento e parcela têm ciclo próprio e não cabem na entidade Conta | CP2 |
| R04 | Sem recorrência e sem parcelamento | Exige geração de lançamentos futuros, que a RN13 proíbe no CP1 | CP2 |
| R05 | Sem recuperação de senha | Exige serviço de e-mail e token de expiração | CP3 |
| R06 | Sem notificações e sem exportação | Exige agendador e geração de arquivo | CP3 |
| R07 | Meta é alimentada manualmente | Derivar das transações exige definir quais contam como aporte | CP2 |
| R08 | Sem soft delete — exclusão é definitiva | Por isso RN08 e RN10 bloqueiam quando há vínculo | — |

---

## Tabela de respostas por violação

| Código | Quando acontece | Regras |
|---|---|---|
| `400` | Requisição malformada | — |
| `401` | Token ausente, inválido ou expirado | RN01 |
| `403` | Recurso público sem permissão de escrita | RN09 |
| `404` | Recurso inexistente **ou de outro usuário** | RN01, RN06 |
| `409` | Conflito de estado: duplicidade ou vínculo | RN02, RN08, RN10, RN15 |
| `422` | Dado válido no formato mas inválido na regra | RN04, RN05, RN11, RN13, RN14 |

A distinção entre `422` e `409` é boa para citar na apresentação: `422` é "esse
dado não pode ser esse"; `409` é "o dado até serve, mas o estado atual do
sistema não permite".

---

## Onde cada regra é testada na demonstração

Roteiro sugerido para o professor ver as regras funcionando, sem precisar de
mais de 6 requisições:

1. Criar despesa com `valor: -50` → **422** (RN04)
2. Criar despesa com categoria "Salário" (tipo RECEITA) → **422** (RN05)
3. Criar transação com `conta_id` de outro usuário → **404** (RN06)
4. Criar transação com data de amanhã → **422** (RN13)
5. Excluir categoria que tem transação → **409** (RN08)
6. `GET /contas` mostrando o saldo bater com a soma do extrato → (RN07)
