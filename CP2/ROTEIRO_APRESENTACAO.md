# Roteiro da apresentação do CP2

Tempo sugerido: **10 a 12 minutos**, mais perguntas.

## 1. Problema e proposta — 45 segundos

O CaixaLivre atende autônomos, freelancers e MEIs que precisam separar finanças
pessoais das finanças do negócio. Toda conta e transação possui a natureza
`PESSOAL` ou `NEGOCIO`, permitindo indicadores úteis para tomada de decisão.

## 2. Evolução desde o CP1 — 1 minuto

- backend reorganizado em routers, services e repositories;
- JWT e isolamento integral dos dados por usuário;
- validações, erros padronizados e regras de integridade;
- frontend funcional, dashboard, testes e integração com Gemini;
- importação revisável de PDF, CSV, OFX e QFX.

## 3. Arquitetura — 1 minuto

Mostrar no repositório:

```text
Nginx/SPA -> FastAPI -> services -> repositories -> PostgreSQL
                                      |
                                      +-> Gemini API
```

Explicar que o frontend nunca acessa o banco nem a chave do Gemini. O backend
aplica autenticação, autorização, regras de negócio e normalização das respostas.

## 4. Demonstração do frontend — 2 minutos

1. Cadastrar ou autenticar o usuário.
2. Criar uma conta e uma transação.
3. Mostrar feedback visual de sucesso e uma validação de erro.
4. Navegar por Contas, Categorias, Transações e Metas.

## 5. Dashboard com dados reais — 1 minuto

Selecionar outubro de 2026 e mostrar:

- saldo das contas;
- receitas, despesas, resultado e taxa de economia;
- gráfico de evolução mensal;
- despesas por categoria;
- separação entre PESSOAL e NEGOCIO.

Explicar que `GET /api/v1/resumo` consolida os dados no backend. O navegador não
baixa todas as transações para recalcular os indicadores.

## 6. Importação inteligente — 2 minutos

1. Abrir **Transações > Importar extrato bancário**.
2. Selecionar `CP2/Extratos públicos para teste.pdf`.
3. Confirmar o aviso de privacidade.
4. Mostrar a prévia com 16 lançamentos, natureza, categoria e confiança.
5. Alterar uma classificação para provar que existe revisão humana.
6. Explicar que nada é persistido antes da confirmação.
7. Repetir a análise para demonstrar a detecção de duplicatas, se os dados forem confirmados.

## 7. LLM ligada ao domínio — 1 minuto

Serviço: Gemini, modelo configurável por `GEMINI_MODEL`.

- Insights recebem somente indicadores agregados.
- CSV/OFX enviam lançamentos normalizados.
- PDF é enviado integralmente após consentimento, pois a leitura é multimodal.
- Senha, JWT, hash e e-mail nunca são enviados.
- Timeout, tratamento de erro e fallback preservam o restante da aplicação.
- A resposta pode variar e exige revisão humana.

## 8. Banco e otimizações — 1 minuto

- modelo em terceira forma normal, sem `usuario_id` duplicado em transação;
- saldo calculado a partir do histórico;
- constraints, chaves estrangeiras e migrações Alembic;
- índices para filtros, unicidade case-insensitive e deduplicação de importações;
- saldo das contas obtido por consulta agregada, evitando N+1;
- paginação e filtros com `X-Total-Count`.

## 9. Testes e documentação — 45 segundos

Executar ao vivo:

```bash
docker compose exec api pytest -q
```

Mostrar `12 passed`, Swagger, GitHub Actions e os documentos `README.md`,
`docs/API.md`, `docs/modelo-dados.md` e `CP2/GUIA_TESTE_PROFESSOR.md`.

## 10. Encerramento — 30 segundos

O CP2 entrega a evolução do backend, uma aplicação integrada, dashboard baseado
em dados reais, banco revisado, testes reproduzíveis e duas utilizações de LLM
ligadas ao problema financeiro. Encerrar mostrando o Trello ou Notion atualizado.

## Divisão sugerida entre integrantes

| Integrante | Parte |
|---|---|
| Thainá Almeida Santos | problema, frontend, dashboard e encerramento |
| Vitor Barbosa Vitorino | backend, API, otimizações e testes |
| Silvio Dela Libera Neto | banco, importação inteligente, Gemini e segurança |

## Plano de contingência

- Se o Gemini estiver indisponível, demonstrar o fallback dos insights e explicar que PDF exige o provedor.
- Se o ambiente perder os dados, usar `CP2/extrato-exemplo.csv` para uma carga rápida.
- Se uma porta estiver ocupada, alterar `FRONTEND_PORT`, `API_PORT` ou `POSTGRES_PORT` no `.env`.
- Manter capturas do dashboard, Swagger, `12 passed` e prévia do PDF para eventual falha de internet.
