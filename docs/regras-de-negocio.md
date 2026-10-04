# Regras de negócio — CaixaLivre

Documento de referência do projeto. Alimenta o [escopo](escopo.md), o
[modelo de dados](modelo-dados.md) e a seção de regras do README.

Cada regra tem: o enunciado, **por que existe**, onde é aplicada no código e o
que a API responde quando é violada. Regra sem justificativa é decoração — daqui
a alguns meses ninguém lembra por que o limite foi posto, e é justamente o
motivo que decide se ele pode ser flexibilizado ou não.

**Numeração:** RN01 a RN14 vieram do levantamento inicial; RN15 a RN17 são
acréscimos deste documento. Os códigos são referenciados nos outros documentos
— **não renumerar**. Regra nova entra com o próximo número livre.

---

## A. Acesso e identidade

### RN01 — Isolamento de dados por usuário

Toda conta, categoria personalizada, transação e meta pertence a exatamente um
usuário. Nenhuma leitura, alteração ou exclusão pode alcançar dado de outro usuário.

**Por quê:** é o que faz a aplicação ser multiusuário de verdade. Sem isso, dois
usuários enxergam o mesmo saldo — na prática, um cliente lendo a vida
financeira do outro.

**Onde:** toda query filtra por `usuario_id` extraído do JWT — **nunca** de um
parâmetro vindo da requisição.

**Violação:** `404 Not Found`, não `403`. Devolver 403 confirma que o recurso
existe e permite descobrir ids de outros usuários por tentativa. Para quem não é
dono, o recurso simplesmente não existe.

### RN02 — E-mail único

Não podem existir dois usuários com o mesmo e-mail. Vale no cadastro e na
alteração de perfil.

**Por quê:** o e-mail é o identificador de login. Com dois usuários no mesmo
e-mail não existe resposta certa para "de quem é essa senha" — o login vira
ambíguo e alguém acaba entrando na conta errada. Não é detalhe de cadastro: é
a chave que sustenta a RN01.

**Por que no banco e não só no service:** verificar antes de inserir tem janela
de corrida. Dois cadastros simultâneos passam os dois pela checagem e os dois
inserem. A constraint é a única garantia que não depende de tempo.

**Onde:** constraint única no banco (a garantia real) mais verificação no
service (para devolver mensagem legível em vez do erro cru do Postgres). O
detalhe da constraint — que é sobre `lower(email)`, não sobre a coluna crua —
está em [modelo-dados.md](modelo-dados.md), seção 4.

**Violação:** `409 Conflict`.

### RN03 — Senha nunca é armazenada nem devolvida em texto

Guardar apenas o hash bcrypt, em campo `senha_hash`. Nenhum schema de resposta
da API pode conter o campo senha, em nenhuma forma.

**Por quê:** senha em texto transforma qualquer vazamento do banco em dano
fora da aplicação. Dump de teste esquecido no repositório, backup, print da
tela do banco — em todos esses casos a senha viaja junto, e
como as pessoas repetem senha, o estrago chega ao e-mail e ao banco do usuário.
Com hash bcrypt, o mesmo vazamento não serve para nada.

Devolver a senha na resposta é a variante mais boba do mesmo problema: ela
passa a aparecer no log do servidor, no cache do navegador e no print do
Swagger. Por isso o schema de saída nem declara o campo — não dá para esquecer
de remover o que nunca esteve lá.

**Onde:** hash no service de usuário; o schema Pydantic de saída simplesmente
não declara o campo — assim é impossível vazar por esquecimento.

**Violação:** é erro de implementação, não de runtime. Vira item obrigatório no
review do módulo de autenticação.

---

## B. Transações

### RN04 — Valor sempre positivo

`valor > 0` em qualquer transação. O sinal do dinheiro vem do **tipo**
(RECEITA soma, DESPESA subtrai), nunca do valor.

**Por quê:** guardar despesa como número negativo parece prático e destrói os
relatórios — toda soma passa a precisar de tratamento especial, e um erro de
sinal vira saldo errado silencioso, sem exceção nem log.

**Onde:** `CHECK (valor > 0)` no banco, mais validação no schema Pydantic de
entrada — o 422 sai antes de a requisição chegar ao banco.

**Violação:** `422 Unprocessable Entity`.

### RN05 — Coerência entre tipo da transação e tipo da categoria

Transação do tipo DESPESA só aceita categoria do tipo DESPESA. Idem para RECEITA.

**Por quê:** sem essa regra dá para lançar "Salário" como despesa, e o relatório
por categoria vira lixo. É também a validação mais fácil de esquecer, porque os
dois campos são válidos isoladamente — o `categoria_id` existe e o `tipo`
existe. É a combinação que não faz sentido, e combinação nenhuma validação de
campo pega sozinha.

**Onde:** service de transação, antes de persistir.

**Violação:** `422`.

### RN06 — Posse dos vínculos

A conta e a categoria informadas na transação devem pertencer ao usuário
autenticado. Exceção: categoria de sistema, que é de todos (ver RN16).

**Por quê:** sem essa checagem, um usuário lança transação na conta de outro
apenas passando o id na mão. É o furo mais comum em CRUD de faculdade.

**Onde:** service de transação, comparando `conta.usuario_id` e
`categoria.usuario_id` com o id que veio do JWT.

**Violação:** `404` para o id que não é dele — mesmo raciocínio da RN01.

### RN13 — Sem lançamento futuro

A `data` da transação não pode ser maior que a data de hoje.

**Por quê:** transação com data futura é "conta a pagar", que é outro conceito,
com regra própria (previsto x realizado) e está fora do escopo atual. Aceitar
data futura agora quebraria o `/resumo`, que passaria a somar dinheiro que ainda
não entrou.

**Onde:** validação no schema Pydantic e no service. Não vira `CHECK`:
`CURRENT_DATE` não é expressão imutável e o Postgres recusa a constraint
(ver [modelo-dados.md](modelo-dados.md), seção 4).

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

**Custo aceito:** uma agregação por consulta. No volume atual é irrelevante.
Se algum dia virar gargalo, a solução é cache — não voltar a coluna mutável.

**Onde:** repository/service de conta.

**Violação:** não se aplica — não há entrada do usuário para recusar. O risco
aqui é de implementação (alguém criar uma coluna `saldo`), então vira item de
review, como na RN03.

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

**Onde:** coluna `natureza` NOT NULL em `conta` e em `transacao`, com enum
nativo do Postgres — valor fora de PESSOAL/NEGOCIO o banco recusa sozinho.

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

**Por quê:** categoria de sistema é uma linha só, compartilhada por todo mundo
(RN16). Sem essa regra, o usuário que renomeia "Alimentação" para "Rango"
renomeia para todos os outros, e quem exclui apaga o seed da aplicação inteira.
O efeito é global e invisível para quem causou — os demais só veem a categoria
sumir do próprio extrato.

O `ON DELETE RESTRICT` da RN08 não cobre esse caso: ele só bloqueia se já
houver transação vinculada. Categoria de sistema recém-criada no seed, ainda
sem uso, seria apagada sem erro nenhum. Quem quer nome próprio cria uma
categoria pessoal — a RN16 deixa as duas conviverem.

**Onde:** service de categoria, checando `usuario_id IS NULL` antes de editar
ou excluir.

**Violação:** `403 Forbidden`. Aqui o 403 é correto — o recurso é público e o
usuário sabe que ele existe; o que falta é permissão.

### RN15 — Nome de categoria único por usuário e tipo

Um usuário não pode ter duas categorias de despesa chamadas "Transporte". Pode
ter uma de despesa e uma de receita com o mesmo nome.

**Por quê:** categoria duplicada quebra exatamente aquilo para que a categoria
existe — o relatório por categoria. Com duas "Transporte" de despesa, o gasto
do mês aparece rachado em duas linhas e nenhuma das duas mostra o total real.
O usuário conclui que gasta menos do que gasta, que é o pior tipo de erro num
app de finanças: não parece um erro.

O escopo `(usuario_id, nome, tipo)` é intencional. "Transporte" como despesa
(gasolina, aplicativo) e "Transporte" como receita (o frete que ele cobra do
cliente) são coisas diferentes na vida do autônomo, e juntar as duas na mesma
linha do relatório seria pior que a duplicata. E o par vale por usuário: o que
o vizinho nomeou não é problema dele.

**Onde:** dois índices únicos parciais — um para categoria de sistema, outro
para categoria de usuário — e sobre `lower(nome)`, para "Transporte" e
"transporte" não passarem como categorias diferentes. O porquê dos dois índices
e do `lower` está em [modelo-dados.md](modelo-dados.md), seções 2 e 4.

**Violação:** `409`.

### RN16 — Categorias de sistema são compartilhadas

Existe um conjunto padrão criado no seed, com `usuario_id` NULL, visível para
todos. A listagem devolve as de sistema mais as personalizadas do usuário.

**Por quê:** usuário recém-cadastrado precisa conseguir lançar a primeira
despesa sem antes ter que cadastrar categoria. Reduz o atrito do primeiro uso e
evita que a aplicação recém-instalada comece com o banco vazio.

**Onde:** `categoria.usuario_id` anulável mais o seed; a listagem filtra
`usuario_id IS NULL OR usuario_id = :usuario_atual`.

**Violação:** tentar editar ou excluir uma delas cai na RN09 — `403`.

---

## E. Metas

### RN11 — Meta válida e cálculo de progresso

`valor_meta > 0`.

```
progresso_percentual = min(100, valor_atual / valor_meta × 100)
valor_restante       = max(0, valor_meta − valor_atual)
```

**Por quê:** `valor_meta = 0` faz o cálculo de progresso dividir por zero e
derrubar o endpoint com 500; meta negativa não quer dizer nada. O `CHECK` no
banco garante que a divisão nunca chega a existir.

O `min(100, …)` e o `max(0, …)` estão ali porque a meta pode ser ultrapassada:
pela R07 o `valor_atual` é digitado à mão, então nada impede o usuário de
guardar mais do que planejou. Sem os limites a API devolve "137% concluído" e
"faltam −350,00", e cada cliente que consumir a API vai ter que tratar isso por
conta — melhor resolver uma vez, aqui.

**Onde:** `CHECK (valor_meta > 0)` no banco; progresso e restante calculados na
leitura, não armazenados — mesmo princípio da RN07. Coluna derivada precisaria
ser reescrita a cada aporte, e um caminho esquecido deixa a barra de progresso
mentindo.

**Violação de `valor_meta <= 0`:** `422`.

### RN12 — Meta atingida

`atingida = valor_atual >= valor_meta`. Campo booleano calculado, devolvido na
resposta.

**Por quê:** para que "essa meta bateu ou não" seja decidido em um lugar só. Se
cada tela que consome a API refizer a comparação, uma delas vai usar `>` no
lugar de `>=`, e a meta atingida na régua — `valor_atual` exatamente igual ao
`valor_meta` — aparece como concluída em uma tela e pendente em outra. É uma
linha de código que evita um bug em dois lugares.

**Onde:** calculado na leitura, no schema de saída da meta — não é coluna, pelo
mesmo motivo da RN07 e da RN11.

**Violação:** não se aplica — é campo derivado, não tem entrada do usuário para
recusar.

---

## F. Valores monetários

### RN17 — Moeda e precisão

Todos os valores em reais (BRL), `NUMERIC(14,2)` no banco e `Decimal` na
aplicação. **Proibido usar float.**

**Por quê:** em ponto flutuante, `0.1 + 0.2` não dá `0.3`. Em sistema
financeiro isso vira centavo perdido que ninguém consegue explicar e que só
aparece depois de muitas transações.

**Onde:** `NUMERIC(14,2)` em toda coluna de valor e `Decimal` nos schemas
Pydantic — a conversão para float não pode acontecer nem na borda da API.

**Violação:** erro de implementação, não de runtime — como na RN03. Vira item
de review: nenhum `float` no caminho do dinheiro.

---

## G. Importação de extratos

### RN18 — Importação exige revisão e não duplica lançamentos

Um extrato é analisado em modo de prévia. A classificação sugerida pela IA ou
pelas regras locais não pode criar conta ou transação até a confirmação do
usuário. Cada lançamento confirmado recebe um hash de data, descrição e valor;
o mesmo hash não pode ser repetido na mesma conta.

**Por quê:** modelos podem classificar incorretamente e bancos podem exportar o
mesmo período mais de uma vez. Revisão humana evita persistir interpretações
erradas, e a deduplicação impede saldo duplicado.

**Onde:** endpoints `/extratos/preview` e `/extratos/confirmar`, service de
importação e índice único parcial em `(conta_id, import_hash)`.

**Violação:** lançamentos repetidos são ignorados e contabilizados na resposta.

---

### RN19 — PDF exige Gemini e confirmação de envio

PDFs bancários são analisados visualmente pelo Gemini porque a extração textual
local pode perder tabelas ou produzir caracteres ilegíveis. Antes do envio, o
frontend deve informar que o documento completo será processado pelo provedor e
pedir confirmação explícita. O limite da aplicação é 10 MB. Sem chave configurada,
o PDF é recusado; CSV/OFX continuam disponíveis com fallback local.

**Por quê:** o documento pode conter agência, conta e outros dados bancários.
Consentimento e limite de tamanho reduzem exposição e abuso acidental.

**Onde:** formulário de importação, schema `ExtratoPreviewRequest` e service de
importação.

---

## Restrições relevantes

Restrição não é regra de negócio. A regra diz como o sistema se comporta; a
restrição diz o que ele deliberadamente **não** faz, e por quê. Registrar a
segunda evita que a ausência seja lida como esquecimento — e deixa claro o que
precisa ser reavaliado quando alguém pedir a funcionalidade.

| # | Restrição | Motivo | Quando |
|---|---|---|---|
| R01 | Sem multi-moeda — apenas BRL | Conversão exige cotação e histórico de câmbio | Não previsto |
| R02 | Sem transferência entre contas | Não é receita nem despesa; exige saída e entrada atômicas com regra própria | Próxima versão |
| R03 | Cartão de crédito não é modelado | Fatura, limite, fechamento e parcela têm ciclo próprio e não cabem na entidade Conta | Próxima versão |
| R04 | Sem recorrência e sem parcelamento | Exige geração de lançamentos futuros, que a RN13 proíbe | Próxima versão |
| R05 | Sem recuperação de senha | Exige serviço de e-mail e token de expiração | Mais adiante |
| R06 | Sem notificações e sem exportação | Exige agendador e geração de arquivo | Mais adiante |
| R07 | Meta é alimentada manualmente | Derivar das transações exige definir quais contam como aporte | Próxima versão |
| R08 | Sem soft delete — exclusão é definitiva | Por isso RN08 e RN10 bloqueiam quando há vínculo | Não previsto |

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

A distinção entre `422` e `409` é o que decide o código na hora de implementar:
`422` é "esse dado não pode ser esse"; `409` é "o dado até serve, mas o estado
atual do sistema não permite".

**RN03, RN07, RN12 e RN17 não têm código de violação**, e isso é proposital:
RN07 e RN12 descrevem campos derivados, sem entrada do usuário para recusar;
RN03 e RN17 são decisões de implementação, cobradas em review e não em runtime.
A RN16 também não tem código próprio — a tentativa de escrita cai na RN09.
