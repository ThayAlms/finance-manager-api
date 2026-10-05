# Guia de avaliação do professor — CaixaLivre CP2

Este documento apresenta um percurso reproduzível para avaliar todos os critérios
do CP2: evolução do backend, frontend integrado, dashboard, otimizações, banco,
Swagger, testes e integração com LLM.

> Branch da entrega: `checkpoint-2`. Data da validação: 05/10/2026.

## 1. Pré-requisitos

- Git;
- Docker Desktop aberto e em execução;
- portas `3000`, `5432` e `8000` disponíveis.

Não é necessário instalar Python, PostgreSQL ou Nginx para o teste principal.

## 2. Executar o projeto

Abra um terminal na pasta raiz do repositório e execute:

```bash
git switch checkpoint-2
docker compose up --build
```

Na primeira execução, o Docker baixará as imagens, criará o banco e aplicará automaticamente as migrações do Alembic. Aguarde a API exibir uma mensagem semelhante a:

```text
Application startup complete.
```

Endereços:

| Recurso | Endereço |
|---|---|
| Aplicação web | <http://localhost:3000> |
| Swagger | <http://localhost:8000/docs> |
| Health check | <http://localhost:8000/health> |
| OpenAPI JSON | <http://localhost:8000/openapi.json> |

O health check deve responder:

```json
{
  "status": "UP"
}
```

## 3. Credenciais de demonstração

Por segurança, o projeto não grava uma senha padrão automaticamente no banco. Em um banco novo, selecione **“Ainda não tenho uma conta”** e faça o cadastro inicial com:

| Campo | Valor |
|---|---|
| Nome | Professor FIAP |
| E-mail/usuário | `professor@caixalivre.com.br` |
| Senha | `Senha@123` |

Se o professor receber o mesmo volume de demonstração utilizado pelo grupo,
também poderá tentar estas contas locais:

| E-mail | Senha |
|---|---|
| `user@example.com` | `Senha@123` |
| `maria@email.com` | `Senha@123` |

Em um clone novo essas contas não existem; nesse caso, use o cadastro indicado
acima. O fluxo de cadastro é parte da demonstração e realiza login automático.

Após o cadastro, a aplicação realiza o login automaticamente. Nas próximas execuções, use o mesmo e-mail e senha na tela de entrada.

> Essas credenciais são apenas para demonstração local. Não devem ser usadas em produção.

## 4. Importação inteligente do extrato

Na tela **Transações**, abra **Importar extrato bancário**. Para demonstrar a
leitura multimodal real, selecione
[`Extratos públicos para teste.pdf`](<Extratos públicos para teste.pdf>).

Preencha:

| Campo | Valor |
|---|---|
| Nome da conta | Conta PJ |
| Tipo | CORRENTE |
| Natureza padrão | NEGOCIO |

Ao usar PDF, confirme o aviso de privacidade: o arquivo completo é enviado ao Gemini. Clique em **Analisar extrato**. A tela deve mostrar uma prévia com categoria,
classificação PESSOAL/NEGOCIO, confiança e aviso sobre o modelo utilizado.
No teste real desse PDF de três páginas, foram identificados 16 lançamentos e o total
de créditos foi igual ao total de débitos. Revise as sugestões e clique em
**Confirmar importação** apenas se quiser persistir os itens selecionados. A
conta e as transações são criadas somente na confirmação.

Arquivos individuais disponíveis para testes adicionais:

| Arquivo | Conteúdo esperado |
|---|---|
| [`Extrato - Banco do brasil.pdf`](<Extrato -  Banco do brasil.pdf>) | primeira página, com movimentações bancárias |
| [`Extrato Itaú V1.pdf`](<Extrato Itaú V1 .pdf>) | segunda página, com movimentações bancárias |
| [`Extrato Itaú V2.pdf`](<Extrato itau V2.pdf>) | terceira página explicativa, sem movimentações; serve como teste negativo |

Para uma demonstração rápida e com números determinísticos de outubro de 2026,
use [`extrato-exemplo.csv`](extrato-exemplo.csv). Ele contém três lançamentos.

Se o mesmo arquivo for analisado novamente para a mesma conta, os lançamentos
devem aparecer como duplicados e não podem ser importados outra vez.

## 5. Carga manual alternativa

Use esta seção somente se não tiver confirmado o CSV de exemplo. O PDF público
contém dados de dezembro de 2022 e não produz os resultados de outubro de 2026
listados abaixo.
Cadastre os dados abaixo pelo frontend. Eles permitem conferir os cálculos sem precisar adivinhar os resultados.

### Contas

| Nome | Tipo | Natureza | Saldo inicial |
|---|---|---|---:|
| Conta PJ | CORRENTE | NEGOCIO | R$ 1.000,00 |
| Carteira pessoal | CARTEIRA | PESSOAL | R$ 300,00 |

### Transações

Use a data `04/10/2026` e as categorias padrão já criadas pelo banco:

| Conta | Categoria | Tipo | Valor | Descrição |
|---|---|---|---:|---|
| Conta PJ | Serviços prestados | RECEITA | R$ 5.000,00 | Projeto entregue |
| Conta PJ | Ferramentas e software | DESPESA | R$ 750,00 | Licenças de trabalho |
| Carteira pessoal | Alimentação | DESPESA | R$ 120,00 | Compras do mês |

A natureza pode permanecer em **“Herdar da conta”**.

### Meta

| Nome | Valor alvo | Valor atual | Prazo |
|---|---:|---:|---|
| Reserva de impostos | R$ 2.500,00 | R$ 625,00 | 31/12/2026 |

## 6. Conferir o dashboard

Na tela **Visão geral**, escolha o período de `01/10/2026` até `31/10/2026`.
Os números seguintes pressupõem o CSV de exemplo confirmado **ou** a carga manual,
nunca os dois ao mesmo tempo.

Resultados esperados:

| Indicador | Resultado |
|---|---:|
| Saldo total usando o CSV de exemplo | R$ 4.130,00 |
| Saldo total usando a carga manual alternativa | R$ 5.430,00 |
| Receitas do período | R$ 5.000,00 |
| Despesas do período | R$ 870,00 |
| Resultado | R$ 4.130,00 |
| Taxa de economia | 82,60% |

Também devem aparecer:

- evolução mensal com receitas e despesas;
- despesas separadas por categoria;
- resultado de `NEGOCIO`: R$ 4.250,00;
- resultado `PESSOAL`: −R$ 120,00.

Na tela **Metas**, a meta “Reserva de impostos” deve aparecer com 25% de progresso.

Esses valores são calculados pela API a partir dos dados reais do PostgreSQL; o frontend não contém valores fixos para o dashboard.

## 7. Testar a inteligência artificial

O teste é feito no card **“Análise inteligente”** do dashboard, por meio do botão **“Gerar análise”**.

### Teste sem chave do Gemini

Não é necessário configurar nada. Clique em **“Gerar análise”**.

Resultado esperado:

- a aplicação apresenta uma análise financeira local;
- a interface informa que `GEMINI_API_KEY` não está configurada;
- dashboard e demais funções continuam funcionando.

Esse comportamento demonstra o tratamento de indisponibilidade e evita que uma dependência externa derrube a aplicação.

### Teste com a LLM real

1. Copie `.env.example` para `.env`.
2. Preencha uma chave válida sem adicioná-la ao Git:

```env
GEMINI_API_KEY=sua-chave-aqui
GEMINI_MODEL=gemini-3.8-flash
GEMINI_TIMEOUT_SECONDS=45
```

3. Recrie a API:

```bash
docker compose up --build -d --force-recreate api
```

4. Volte ao dashboard e clique em **“Gerar análise”**.

Resultado esperado:

- `gerado_por_ia` será verdadeiro na resposta da API;
- o frontend exibirá a análise e o modelo utilizado;
- o texto será baseado nos indicadores do período selecionado.

Nos insights, a LLM recebe somente dados financeiros agregados. Na importação
CSV/OFX, recebe os lançamentos normalizados. Na importação PDF, o documento
completo é enviado após o aviso e a confirmação do usuário, pois a leitura visual
é necessária para interpretar tabelas e fontes codificadas. Senha, hash, JWT e
e-mail da aplicação não são enviados. A resposta é educativa e não representa
aconselhamento financeiro profissional.

Também é possível testar diretamente no Swagger:

```text
POST /api/v1/insights?inicio=2026-10-01&fim=2026-10-31
```

Antes, faça login em `POST /api/v1/auth/login`, copie o `access_token` e use o botão **Authorize** do Swagger com o token.

## 8. Testar filtros e paginação

No Swagger, execute `GET /api/v1/transacoes` com:

```text
inicio=2026-10-01
fim=2026-10-31
tipo=DESPESA
natureza=PESSOAL
offset=0
limit=20
```

A resposta deve conter somente a despesa da carteira pessoal. O cabeçalho `X-Total-Count` informa o total encontrado antes da paginação.

## 9. Testar validações e segurança

| Teste | Resultado esperado |
|---|---|
| Acessar `/api/v1/contas` sem token | `401 Unauthorized` |
| Cadastrar valor negativo em transação | `422 Unprocessable Entity` |
| Cadastrar transação futura | `422 Unprocessable Entity` |
| Usar categoria de receita em despesa | `422 Unprocessable Entity` |
| Criar `Conta Principal` e depois `conta principal` | `409 Conflict` |
| Criar `Reserva` e depois `reserva` | `409 Conflict` |
| Informar data inicial posterior à final | `422 Unprocessable Entity` |
| Tentar consultar conta pertencente a outro usuário | `404 Not Found` |

Os erros seguem uma estrutura padronizada com data, status, tipo, mensagem, caminho e erros de campo quando aplicável.

## 10. Executar os testes automatizados

Com os containers ativos, execute em qualquer sistema operacional:

```bash
docker compose exec api pytest -q
```

Os testes estão incluídos na imagem da API, portanto esse comando não exige
Python instalado no computador do avaliador.

Resultado esperado:

```text
12 passed
```

## 11. Verificar a migração do banco

Com os containers ativos:

```bash
docker compose exec api alembic current
```

Resultado esperado:

```text
0003 (head)
```

As migrações `0002` e `0003` implementam índices case-insensitive, unicidade de metas, índices do dashboard e deduplicação de extratos.

## 12. Checklist visual antes da banca

Esta etapa deve ser executada manualmente em desktop e em uma largura de celular:

- [ ] cadastro, login e logout funcionam;
- [ ] menu navega entre todas as telas;
- [ ] formulários exibem sucesso e erros legíveis;
- [ ] dashboard atualiza quando o período muda;
- [ ] gráficos não apresentam texto cortado ou sobreposto;
- [ ] importação mostra prévia antes de habilitar a confirmação;
- [ ] seletores de PF/PJ e categoria podem ser alterados;
- [ ] duplicatas aparecem desabilitadas;
- [ ] insight identifica se usou Gemini ou fallback local;
- [ ] layout permanece utilizável em tela estreita.

## 13. Mapa do barema para evidências

| Critério | Demonstração | Evidência técnica |
|---|---|---|
| Backend | cadastro, erros e isolamento | `app/services`, schemas, JWT e testes |
| Frontend | CRUD, navegação e feedback | `frontend/app.js` e `frontend/styles.css` |
| Dashboard | cards e gráficos com período | `GET /api/v1/resumo` |
| Otimização | filtros, paginação e saldo agregado | repositories e `X-Total-Count` |
| Banco | integridade, índices e normalização | Alembic `0001`, `0002`, `0003` e DER |
| Documentação | instalação, arquitetura e endpoints | README, `docs/` e Swagger |
| Testes | executar `pytest` no container | 12 testes e GitHub Actions |
| LLM | insight e importação multimodal | Gemini, revisão humana, timeout e fallback |

## 14. Material da apresentação e gestão

- [`ROTEIRO_APRESENTACAO.md`](ROTEIRO_APRESENTACAO.md): ordem, tempo e falas sugeridas.
- [`PLANO_TRELLO_NOTION.md`](PLANO_TRELLO_NOTION.md): cartões prontos para copiar ao quadro externo.
- [`AUDITORIA_BAREMA.md`](AUDITORIA_BAREMA.md): situação de cada critério e pendências externas.

O link ou a captura do Trello/Notion e o arquivo final de slides devem ser
adicionados antes do envio. Esses itens dependem das contas e da identidade
visual escolhidas pelo grupo.

## 15. Encerrar a aplicação

Para parar os containers preservando os dados cadastrados:

```bash
docker compose down
```

Para apagar o banco de demonstração e começar novamente do zero:

```bash
docker compose down -v
```

> O comando com `-v` remove definitivamente todos os dados locais do PostgreSQL.

## 16. Solução rápida de problemas

| Problema | Solução |
|---|---|
| Docker não responde | Abrir o Docker Desktop e aguardar o mecanismo iniciar |
| Porta ocupada | Alterar `FRONTEND_PORT`, `API_PORT` ou `POSTGRES_PORT` no `.env` |
| Dados anteriores interferem no teste | Executar `docker compose down -v` e subir novamente |
| Dashboard vazio | Conferir o período e cadastrar transações dentro dele |
| Insight usa resposta local | Configurar `GEMINI_API_KEY` e recriar o container da API |
| PDF retorna `422` mesmo com chave | Conferir validade, permissão e cota da chave; o provedor pode estar temporariamente indisponível |
| Token expirado | Sair da aplicação e realizar login novamente |
