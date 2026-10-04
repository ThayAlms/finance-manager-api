# Guia de teste do professor — CaixaLivre CP2

Este documento apresenta o caminho mais rápido para executar e avaliar o projeto completo: frontend, API, banco de dados, dashboard, testes automatizados e integração com LLM.

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

Após o cadastro, a aplicação realiza o login automaticamente. Nas próximas execuções, use o mesmo e-mail e senha na tela de entrada.

> Essas credenciais são apenas para demonstração local. Não devem ser usadas em produção.

## 4. Carga manual para demonstrar o dashboard

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

## 5. Conferir o dashboard

Na tela **Visão geral**, escolha o período de `01/10/2026` até `31/10/2026`.

Resultados esperados:

| Indicador | Resultado |
|---|---:|
| Saldo total | R$ 5.430,00 |
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

## 6. Testar a inteligência artificial

O teste é feito no card **“Análise inteligente”** do dashboard, por meio do botão **“Gerar análise”**.

### Teste sem chave da OpenAI

Não é necessário configurar nada. Clique em **“Gerar análise”**.

Resultado esperado:

- a aplicação apresenta uma análise financeira local;
- a interface informa que `OPENAI_API_KEY` não está configurada;
- dashboard e demais funções continuam funcionando.

Esse comportamento demonstra o tratamento de indisponibilidade e evita que uma dependência externa derrube a aplicação.

### Teste com a LLM real

1. Copie `.env.example` para `.env`.
2. Preencha uma chave válida sem adicioná-la ao Git:

```env
OPENAI_API_KEY=sua-chave-aqui
OPENAI_MODEL=gpt-6-astra
OPENAI_TIMEOUT_SECONDS=20
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

A LLM recebe somente dados financeiros agregados. O sistema não envia senha, hash, JWT, e-mail nem lançamentos individuais. A resposta é educativa e não representa aconselhamento financeiro profissional.

Também é possível testar diretamente no Swagger:

```text
POST /api/v1/insights?inicio=2026-10-01&fim=2026-10-31
```

Antes, faça login em `POST /api/v1/auth/login`, copie o `access_token` e use o botão **Authorize** do Swagger com o token.

## 7. Testar filtros e paginação

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

## 8. Testar validações e segurança

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

## 9. Executar os testes automatizados

### Windows PowerShell

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pytest -q
```

### Linux ou macOS

```bash
python3 -m venv .venv
./.venv/bin/python -m pip install -r requirements.txt
./.venv/bin/python -m pytest -q
```

Resultado esperado:

```text
10 passed
```

## 10. Verificar a migração do banco

Com os containers ativos:

```bash
docker compose exec api alembic current
```

Resultado esperado:

```text
0002 (head)
```

A migração `0002` implementa índices case-insensitive, unicidade de metas e índices usados pelos filtros do dashboard.

## 11. Encerrar a aplicação

Para parar os containers preservando os dados cadastrados:

```bash
docker compose down
```

Para apagar o banco de demonstração e começar novamente do zero:

```bash
docker compose down -v
```

> O comando com `-v` remove definitivamente todos os dados locais do PostgreSQL.

## 12. Solução rápida de problemas

| Problema | Solução |
|---|---|
| Docker não responde | Abrir o Docker Desktop e aguardar o mecanismo iniciar |
| Porta ocupada | Alterar `FRONTEND_PORT`, `API_PORT` ou `POSTGRES_PORT` no `.env` |
| Dados anteriores interferem no teste | Executar `docker compose down -v` e subir novamente |
| Dashboard vazio | Conferir o período e cadastrar transações dentro dele |
| Insight usa resposta local | Configurar `OPENAI_API_KEY` e recriar o container da API |
| Token expirado | Sair da aplicação e realizar login novamente |
