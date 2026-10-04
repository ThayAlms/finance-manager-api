# Auditoria do CP2 contra o barema

**Data da auditoria:** 04/10/2026

**Branch auditada:** `checkpoint-2`

**Commit técnico:** `7a388b7`

## Resultado executivo

A implementação cobre tecnicamente os **8 critérios pontuados** do trecho de barema recebido. Entretanto, o pacote de entrega ainda não deve ser apresentado como pronto para nota máxima porque faltam evidências externas e de apresentação.

## Critérios pontuados

| Critério | Situação | Evidência | Avaliação |
|---|---|---|---:|
| Evolução e qualidade do backend | Atendido | Schemas Pydantic, JWT, isolamento por usuário, erros padronizados e regras em `app/services` | 0,5/0,5 |
| Frontend e integração | Atendido, com QA manual pendente | SPA dinâmica, CRUD principal, importação de extratos, navegação, toasts e estados vazios | 2,0/2,0* |
| Dashboard | Atendido | `GET /api/v1/resumo`, cards, gráficos, categorias e separação pessoal/negócio | 2,0/2,0 |
| Otimização da API | Atendido | Saldo agregado sem N+1, filtros, `offset`, `limit`, `X-Total-Count` e índices adicionais | 0,5/0,5 |
| Banco | Atendido | Migrações `0002` e `0003`, índices case-insensitive, agregações e deduplicação de extratos | 1,0/1,0 |
| Documentação e Swagger | Atendido | README, `docs/API.md`, exemplos HTTP e schemas/response models do FastAPI | 0,5/0,5 |
| Testes iniciais | Atendido | 11 testes aprovados, incluindo dashboard, filtros, normalização, importação e LLM | 1,0/1,0 |
| Integração da LLM | Atendido | `POST /api/v1/insights`, importação inteligente, Gemini API validada em execução real, timeout e fallback | 1,0/1,0 |

**Cobertura técnica estimada:** `8,5/8,5` nos valores exibidos no texto recebido. O asterisco restante indica somente a conferência visual final em navegador antes da apresentação.

## Evidências da LLM exigidas pelo enunciado

| Pergunta | Resposta do projeto |
|---|---|
| Modelo ou serviço | Gemini API; modelo configurável por `GEMINI_MODEL`, com padrão `gemini-3.8-flash` |
| Finalidade | Produzir uma análise educativa e contextual dos resultados financeiros do período |
| Dados enviados | Insights: resumo agregado. Importação: data, descrição, valor e tipo já extraídos localmente |
| Dados não enviados | Senha, hash, JWT, e-mail, conteúdo bruto do arquivo e nome/número da conta |
| Resposta obtida | Texto curto com até três observações práticas, marcado com `gerado_por_ia` e o modelo usado |
| Uso no frontend | Exibição no card “Análise inteligente” do dashboard |
| Limitações | Resposta não determinística, dependência do provedor, custo, latência e possibilidade de indisponibilidade |
| Mitigações | Instruções restritivas, timeout, tratamento de falha, fallback local e aviso de caráter educativo |

## Otimizações para explicar na apresentação

1. A CP1 calculava o saldo com uma consulta por conta. A CP2 usa subconsulta agregada e lista todas as contas com seus saldos em uma única consulta.
2. A listagem de transações agora aceita período, tipo, natureza, `offset` e `limit`, além de retornar `X-Total-Count`.
3. O dashboard consolida os dados no backend, evitando que o navegador baixe todas as transações para recalcular indicadores.
4. As migrações `0002` e `0003` adicionam índices para filtros, unicidade sem diferenciar caixa e deduplicação de extratos.
5. Os erros de validação e negócio mantêm um contrato consistente com status, mensagem, caminho e erros por campo.

## Pendências para afirmar “pronto para nota máxima”

- [ ] Publicar a branch `checkpoint-2` no GitHub e abrir/mesclar o PR conforme a estratégia do grupo.
- [ ] Atualizar Trello ou Notion e incluir no README o link ou uma captura que possa ser demonstrada.
- [ ] Criar a apresentação e ensaiar o roteiro de demonstração.
- [ ] Fazer QA visual manual em desktop e celular: login, formulários, navegação, gráficos, erros e feedback.
- [ ] Executar uma chamada real de LLM com uma chave de desenvolvimento e registrar evidência sem expor a chave.
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
