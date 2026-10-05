# Auditoria do CP2 contra o barema

**Data da auditoria:** 04/10/2026

**Branch auditada:** `checkpoint-2`

**Estado técnico validado em:** 05/10/2026

## Resultado executivo

A implementação cobre tecnicamente os **8 critérios pontuados** do trecho de
barema recebido. A nota final depende da avaliação do professor e de três ações
externas: publicação da branch, evidência de Trello/Notion e apresentação final.

## Critérios pontuados

| Critério | Situação | Evidência | Avaliação |
|---|---|---|---:|
| Evolução e qualidade do backend | Atendido | Schemas Pydantic, JWT, isolamento por usuário, erros padronizados e regras em `app/services` | 0,5/0,5 |
| Frontend e integração | Atendido, com checklist visual final | SPA dinâmica, CRUD principal, importação de extratos, navegação, toasts e estados vazios | 2,0/2,0* |
| Dashboard | Atendido | `GET /api/v1/resumo`, cards, gráficos, categorias e separação pessoal/negócio | 2,0/2,0 |
| Otimização da API | Atendido | Saldo agregado sem N+1, filtros, `offset`, `limit`, `X-Total-Count` e índices adicionais | 0,5/0,5 |
| Banco | Atendido | Migrações `0002` e `0003`, índices case-insensitive, agregações e deduplicação de extratos | 1,0/1,0 |
| Documentação e Swagger | Atendido | README, `docs/API.md`, exemplos HTTP e schemas/response models do FastAPI | 0,5/0,5 |
| Testes iniciais | Atendido | 13 testes, incluindo verificação direta de que senha não é armazenada em texto puro | 1,0/1,0 |
| Integração da LLM | Atendido | `POST /api/v1/insights`, importação inteligente, Gemini API validada em execução real, timeout e fallback | 1,0/1,0 |

**Cobertura técnica estimada:** `8,5/8,5` nos valores exibidos no texto recebido. O asterisco restante indica somente a conferência visual final em navegador antes da apresentação.

## Evidências da LLM exigidas pelo enunciado

| Pergunta | Resposta do projeto |
|---|---|
| Modelo ou serviço | Gemini API; modelo configurável por `GEMINI_MODEL`, com padrão `gemini-3.8-flash` |
| Finalidade | Produzir uma análise educativa e contextual dos resultados financeiros do período |
| Dados enviados | Insights: resumo agregado. CSV/OFX: lançamentos normalizados. PDF: documento completo após confirmação explícita, necessário para leitura visual |
| Dados não enviados | Senha, hash, JWT, e-mail e credenciais da aplicação; no PDF, dados impressos no próprio documento podem ser processados pelo provedor |
| Resposta obtida | Texto curto com até três observações práticas, marcado com `gerado_por_ia` e o modelo usado |
| Uso no frontend | Exibição no card “Análise inteligente” do dashboard |
| Limitações | Resposta não determinística, dependência do provedor, custo, latência e possibilidade de indisponibilidade |
| Mitigações | Instruções restritivas, timeout, tratamento de falha, fallback local e aviso de caráter educativo |

Validação prática em 04/10/2026: o PDF de 3 páginas em
`CP2/Extratos públicos para teste.pdf` foi lido pelo Gemini em modo multimodal e
produziu uma prévia estruturada com 16 lançamentos. Nenhuma transação foi gravada.
Em 05/10/2026, uma nova tentativa encontrou indisponibilidade externa; a API
respondeu com erro controlado para PDF e utilizou fallback local nos insights.

## Otimizações para explicar na apresentação

1. A CP1 calculava o saldo com uma consulta por conta. A CP2 usa subconsulta agregada e lista todas as contas com seus saldos em uma única consulta.
2. A listagem de transações agora aceita período, tipo, natureza, `offset` e `limit`, além de retornar `X-Total-Count`.
3. O dashboard consolida os dados no backend, evitando que o navegador baixe todas as transações para recalcular indicadores.
4. As migrações `0002` e `0003` adicionam índices para filtros, unicidade sem diferenciar caixa e deduplicação de extratos.
5. Os erros de validação e negócio mantêm um contrato consistente com status, mensagem, caminho e erros por campo.

## Pendências externas antes da entrega

- [ ] Publicar a branch `checkpoint-2` no GitHub e abrir/mesclar o PR conforme a estratégia do grupo.
- [ ] Atualizar Trello ou Notion e incluir no README o link ou uma captura que possa ser demonstrada.
- [ ] Criar a apresentação e ensaiar o roteiro de demonstração.
- [ ] Fazer QA visual manual em desktop e celular: login, formulários, navegação, gráficos, erros e feedback.
- [x] Executar uma chamada real de LLM com uma chave de desenvolvimento e registrar evidência sem expor a chave.
- [ ] Confirmar com o professor a conversão do barema exibido, cuja soma é 8,5, para os 30 pontos informados no título.

## Roteiro mínimo da demonstração

1. Comparar CP1 e CP2 e mostrar a organização do backend.
2. Subir o projeto com Docker e abrir aplicação, Swagger e health check.
3. Cadastrar usuário, conta, categoria, transações e meta pelo frontend.
4. Demonstrar que o dashboard muda com dados reais e filtros de período.
5. Explicar consulta agregada, paginação, filtros e índices das migrações `0002` e `0003`.
6. Executar os testes e mostrar o pipeline de CI.
7. Gerar um insight, explicar os dados enviados e demonstrar o fallback.
8. Exibir o Trello/Notion atualizado e concluir com limitações e próximos passos.

O roteiro detalhado está em [`ROTEIRO_APRESENTACAO.md`](ROTEIRO_APRESENTACAO.md)
e os cartões para o quadro externo estão em
[`PLANO_TRELLO_NOTION.md`](PLANO_TRELLO_NOTION.md).
