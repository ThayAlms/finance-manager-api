# Deploy da solução na Vercel

## Arquitetura publicada

O arquivo `Dockerfile.vercel` define um contêiner HTTP com Python 3.12, FastAPI,
Alembic e o frontend estático. A Vercel constrói essa imagem, executa o servidor
na porta indicada por `PORT` e publica a solução em um único domínio:

- `/` entrega a aplicação web;
- `/api/v1` expõe a API REST;
- `/docs` disponibiliza o Swagger;
- `/health` consulta a API e o PostgreSQL.

O `vercel.json` seleciona `gru1`, região da Vercel em São Paulo. O banco permanece
fora do contêiner, pois as instâncias são stateless. A opção recomendada para o
projeto é PostgreSQL Neon instalado pelo Marketplace da Vercel.

## Publicar pelo GitHub

1. Enviar a branch final para
   `https://github.com/ThayAlms/finance-manager-api`.
2. Acessar `https://vercel.com/new`, importar o repositório e manter a raiz do
   projeto como **Root Directory**.
3. Confirmar que a Vercel detectou `Dockerfile.vercel`. Não informar Build
   Command nem Output Directory.
4. No projeto, abrir **Storage** ou **Marketplace**, instalar o Neon e conectar o
   banco ao projeto. Confirmar que a integração criou `DATABASE_URL`.
5. Em **Settings > Environment Variables**, cadastrar os valores da tabela
   abaixo para Production e, se necessário, Preview.
6. Executar o deploy. Na inicialização, o contêiner aplica
   `alembic upgrade head` e inicia o Uvicorn.
7. Abrir `/health`, `/`, `/docs` e executar cadastro, login, conta e transação.
8. Copiar a URL real para este arquivo e para `CP3/README.md`.

**Endereço do deploy:** `PENDENTE_APOS_PUBLICACAO_NA_VERCEL`

## Variáveis de produção

| Variável | Obrigatória | Configuração na Vercel |
|---|---:|---|
| `DATABASE_URL` | sim | fornecida pela integração PostgreSQL/Neon; preferir conexão com pooling |
| `SECRET_KEY` | sim | valor longo e aleatório, marcado como Sensitive |
| `ENVIRONMENT` | sim | `production` |
| `PORT` | automática | injetada pela Vercel; não cadastrar manualmente |
| `CORS_ORIGINS` | recomendada | URL final `https://SEU-PROJETO.vercel.app` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | não | `60` |
| `GEMINI_API_KEY` | não | segredo opcional para PDFs e insights por IA |
| `GEMINI_MODEL` | não | `gemini-3.8-flash` |
| `GEMINI_TIMEOUT_SECONDS` | não | `45` |

A configuração aceita URLs `postgres://` e `postgresql://` fornecidas por
provedores externos e seleciona automaticamente o driver `psycopg` instalado.

## Publicar pela CLI

Alternativa ao painel, depois de instalar e autenticar a Vercel CLI:

```bash
vercel link
vercel env ls production
vercel --prod
```

Para cadastrar segredos pela CLI, permitir que o comando solicite o valor em vez
de colocá-lo no histórico do terminal:

```bash
vercel env add SECRET_KEY production --sensitive
vercel env add GEMINI_API_KEY production --sensitive
```

O banco deve ser conectado pelo Marketplace antes do deploy de produção.

## Verificação pós-deploy

```bash
curl -f https://URL-REAL.vercel.app/health
curl -I https://URL-REAL.vercel.app/
curl -I https://URL-REAL.vercel.app/docs
```

Resultado esperado do health check:

```json
{"status":"UP"}
```

Depois, cadastrar um usuário pela interface, criar uma conta e lançar uma
receita e uma despesa. O dashboard deve recalcular saldo, resultado e taxa de
economia.

## Validação local da imagem usada pela Vercel

```bash
docker build -f Dockerfile.vercel -t caixalivre-vercel .
```

O Compose continua sendo a execução local recomendada porque já conecta Nginx,
API e PostgreSQL:

```bash
docker compose up -d --build
docker compose ps
curl http://localhost:8000/health
```

## Segurança

- `.env` e `.vercel/` estão ignorados pelo Git.
- `SECRET_KEY`, conexão do banco e chave Gemini ficam nas variáveis da Vercel.
- O frontend e a API usam o mesmo domínio, reduzindo a superfície de CORS.
- A conexão PostgreSQL deve usar TLS e pooling quando oferecidos pelo provedor.
- Prints de evidência não devem mostrar valores de variáveis ou connection
  strings.

## Limitações e operação

- O contêiner da Vercel é stateless; todo dado persistente fica no PostgreSQL.
- A primeira requisição pode ter latência maior quando uma instância inicia.
- A região do banco deve ficar em São Paulo ou o mais próximo possível de
  `gru1` para reduzir latência.
- Para este checkpoint, as migrações rodam no startup do contêiner. Em uma
  operação com muitas instâncias, elas devem migrar para uma etapa controlada de
  release para evitar execuções simultâneas.
- Limites e cobrança dependem dos planos vigentes da Vercel e do provedor do
  banco.
