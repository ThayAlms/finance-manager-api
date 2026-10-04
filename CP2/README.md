# CP2

**Data da entrega:** 06/10/2026

- [Enunciado recebido](ENUNCIADO.md)
- [Auditoria contra o barema](AUDITORIA_BAREMA.md)
- [Guia de teste do professor](GUIA_TESTE_PROFESSOR.md)

## Entregáveis

- [x] Frontend do aplicativo
- [x] Dashboard de controle
- [x] Otimização da API
- [x] Normalização do banco
- [x] Ajuste da documentação
- [x] Testes iniciais
- [x] Aplicação de LLM
- [ ] Trello ou Notion atualizado
- [ ] Apresentação do CP2
- [ ] Branch publicada no GitHub

## Evidências

| Entrega | Implementação |
|---|---|
| Frontend | SPA responsiva em [`frontend`](../frontend), servida por Nginx e integrada à API |
| Dashboard | Cards, evolução mensal, despesas por categoria e divisão pessoal/negócio usando `GET /api/v1/resumo` |
| Otimização | Saldo das contas calculado em consulta agregada; filtros e paginação em transações |
| Banco | Migração [`0002_normalizacao_cp2.py`](../alembic/versions/0002_normalizacao_cp2.py) com índices funcionais e novos índices de consulta |
| Documentação | README, documentação da API, exemplos HTTP e comandos atualizados |
| Testes | 10 testes automatizados cobrindo CP1 e os fluxos novos da CP2 |
| LLM | `POST /api/v1/insights` via OpenAI Responses API, com timeout e fallback local |

## Critérios de aceite

- O usuário consegue se cadastrar, autenticar e navegar pelo frontend.
- O dashboard apresenta apenas dados do usuário autenticado no período escolhido.
- Receitas, despesas, resultado, saldo e taxa de economia são calculados pela API.
- Contas são listadas sem uma consulta adicional de saldo por conta.
- Nomes de contas, categorias e metas, além de e-mails, são únicos sem diferenciar maiúsculas e minúsculas.
- A aplicação continua útil sem `OPENAI_API_KEY`; nesse caso, informa que utilizou análise local.
- API, PostgreSQL e frontend sobem com `docker compose up --build`.

## Validação realizada

- `pytest -q`: **10 testes aprovados**.
- `node --check frontend/app.js`: JavaScript válido.
- `docker compose config --quiet`: configuração válida.
- Builds Docker da API e do frontend concluídos.
- PostgreSQL inicializado com Alembic em `0002 (head)`.
- Smoke test em containers: saúde `UP`, frontend HTTP `200`, cadastro, login e resumo aprovados.

> A conferência visual interativa deve ser repetida em um navegador antes da apresentação final, pois o ambiente de automação usado na implementação não disponibilizou uma superfície de navegador controlável.
