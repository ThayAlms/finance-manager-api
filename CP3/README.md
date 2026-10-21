# Checkpoint 3 - CaixaLivre

**Entrega:** 27/10/2026
**Tema:** testes, deploy, containerização e monetização

## Resultado da entrega

O CaixaLivre está preparado para execução local com Docker Compose e publicação
em serviço Docker com PostgreSQL gerenciado. A suíte possui 15 testes
automatizados e documenta 11 cenários de sucesso, erro, segurança e integração.
O material de entrega inclui proposta de monetização, quadro ágil, roteiro e
apresentação.

## Integrantes

| Integrante | RM |
|---|---:|
| Thainá Almeida Santos | 569110 |
| Vitor Barbosa Vitorino | 570475 |
| Silvio Dela Libera Neto | 572632 |

## Tema e objetivo

O CaixaLivre ajuda autônomos, freelancers e MEIs a separar finanças pessoais e
do negócio. A solução oferece contas, categorias, transações, metas, dashboard,
importação revisável de extratos e insights financeiros educativos.

## Arquitetura

```text
Navegador
   |
   | HTTPS
   v
FastAPI + SPA no mesmo contêiner
   |-- /                  frontend HTML/CSS/JS
   |-- /api/v1            API REST com JWT
   |-- /docs              Swagger
   `-- /health            API + consulta ao banco
            |
            v
      PostgreSQL 16

Gemini API (opcional) <--- somente pelo backend
```

Localmente, o Compose executa Nginx, API e PostgreSQL em serviços separados. Na
Vercel, `Dockerfile.vercel` publica a SPA e a API no mesmo domínio e conecta o
contêiner a um PostgreSQL do Marketplace.

## Links

- **GitHub:** https://github.com/ThayAlms/finance-manager-api
- **Trello do grupo:** https://trello.com/b/9r4U0gNO/controle-financeiro-cps
- **Espelho auditável do quadro:** [docs/QUADRO_AGIL.md](docs/QUADRO_AGIL.md)
- **Deploy:** `PENDENTE_APOS_PUBLICACAO_NA_VERCEL`
- **Apresentação:** [Apresentacao_CP3_CaixaLivre.pptx](Apresentacao_CP3_CaixaLivre.pptx)
- **Roteiro da demonstração:** [ROTEIRO_DEMO.md](ROTEIRO_DEMO.md)

O endereço do deploy deve ser preenchido somente depois que a equipe publicar e
validar a URL real. As instruções estão em [docs/DEPLOY.md](docs/DEPLOY.md).

## Execução com Docker

```bash
docker compose up --build
```

Serviços locais:

- frontend: http://localhost:3000
- API: http://localhost:8000
- Swagger: http://localhost:8000/docs
- health check: http://localhost:8000/health

Verificação:

```bash
docker compose ps
docker compose logs api
docker compose exec api pytest -q
```

## Testes

Execução direta, quando Python 3.12 e as dependências estão instalados:

```bash
python -m pytest -q
```

Resultado registrado em 20/10/2026: **15 testes aprovados**. A suíte cobre
cadastro, login, senha com BCrypt, autorização, contas, transações, metas,
dashboard, filtros, erros de validação, importação CSV/PDF, deduplicação,
fallback sem LLM, contrato OpenAPI, frontend no serviço de produção e URL do
banco em ambiente de nuvem.

Detalhes e resultados esperados/obtidos:
[docs/CENARIOS_TESTE.md](docs/CENARIOS_TESTE.md).

## Variáveis de ambiente

Copiar `.env.example` para `.env` no desenvolvimento. O arquivo `.env` é
ignorado pelo Git.

| Variável | Finalidade | Segredo |
|---|---|---:|
| `DATABASE_URL` | conexão SQLAlchemy com PostgreSQL | sim em produção |
| `SECRET_KEY` | assinatura dos tokens JWT | sim |
| `CORS_ORIGINS` | origens permitidas | não |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | duração do token | não |
| `GEMINI_API_KEY` | habilita PDF e insights por IA | sim, opcional |
| `GEMINI_MODEL` | seleciona o modelo | não |

Nunca versionar valores reais de `SECRET_KEY`, senha do banco ou chave Gemini.

## Deploy

O `Dockerfile.vercel` define o serviço HTTP em contêiner, e o `vercel.json`
seleciona a região `gru1` em São Paulo. O PostgreSQL deve ser criado pelo
Marketplace da Vercel, que injeta a conexão no projeto. A publicação exige
conectar o repositório à conta do grupo. Consulte
[docs/DEPLOY.md](docs/DEPLOY.md).

## Monetização

Modelo freemium com plano Pro de **R$ 19,90/mês**. Em uma simulação com 500
usuários cadastrados e 50 assinantes, a receita bruta mensal chega a R$ 995,00;
após R$ 499,50 de custos operacionais estimados, restam R$ 495,50 antes da mão
de obra. As premissas e o ponto de equilíbrio estão em
[docs/MONETIZACAO.md](docs/MONETIZACAO.md).

## Limitações conhecidas

- a URL pública depende da publicação na conta do grupo;
- o plano gratuito do provedor pode atrasar o primeiro acesso;
- a leitura de PDF depende de chave e disponibilidade do Gemini;
- os custos de infraestrutura e LLM são estimativas que exigem validação real;
- gateway de pagamento não faz parte do escopo do checkpoint;
- teste com cliente é opcional e ainda não foi registrado.

## Índice da entrega

- [Cenários e evidências de teste](docs/CENARIOS_TESTE.md)
- [Deploy e verificação](docs/DEPLOY.md)
- [Proposta de monetização](docs/MONETIZACAO.md)
- [Quadro ágil](docs/QUADRO_AGIL.md)
- [Roteiro da demonstração](ROTEIRO_DEMO.md)
- [Checklist final](VALIDACAO_FINAL.md)
- [Auditoria do barema](AUDITORIA_BAREMA.md)

## Atendimento ao barema

| Critério | Evidência | Situação |
|---|---|---|
| Testes funcionais e integração | 15 testes e matriz com 11 cenários | atendido |
| Evidências e tratamento de falhas | resultados, erros 422/404/409, correções e logs Docker | atendido |
| Deploy e funcionamento | `Dockerfile.vercel`, configuração regional e guia | preparado; publicação externa pendente |
| Containerização | Dockerfiles, Compose, health check e comandos | validado em 20/10/2026 |
| Monetização | público, preço, receita, custos e viabilidade | atendido |
| GitHub e organização ágil | repositório, integrantes e quadro versionado | atendido |
| Apresentação e demonstração | PPTX e roteiro cronometrado | atendido |
