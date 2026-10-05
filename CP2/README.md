# CP2

**Data da entrega:** 06/10/2026

- [Enunciado recebido](ENUNCIADO.md)
- [Auditoria contra o barema](AUDITORIA_BAREMA.md)
- [Guia de teste do professor](GUIA_TESTE_PROFESSOR.md)
- [Roteiro da apresentação](ROTEIRO_APRESENTACAO.md)
- [Plano para Trello ou Notion](PLANO_TRELLO_NOTION.md)
- [Evidências de validação](EVIDENCIAS_VALIDACAO.md)

## Entregáveis

- [x] Frontend do aplicativo
- [x] Dashboard de controle
- [x] Otimização da API
- [x] Normalização do banco
- [x] Ajuste da documentação
- [x] Testes iniciais
- [x] Aplicação de LLM
- [ ] Trello ou Notion atualizado
- [x] Roteiro completo da apresentação
- [ ] Arquivo final de slides criado pelo grupo
- [ ] Branch publicada no GitHub

## Evidências

| Entrega | Implementação |
|---|---|
| Frontend | SPA responsiva em [`frontend`](../frontend), servida por Nginx e integrada à API |
| Dashboard | Cards, evolução mensal, despesas por categoria e divisão pessoal/negócio usando `GET /api/v1/resumo` |
| Otimização | Saldo das contas calculado em consulta agregada; filtros e paginação em transações |
| Banco | Migrações [`0002_normalizacao_cp2.py`](../alembic/versions/0002_normalizacao_cp2.py) e [`0003_importacao_extratos.py`](../alembic/versions/0003_importacao_extratos.py) |
| Documentação | README, documentação da API, exemplos HTTP e comandos atualizados |
| Testes | 12 testes automatizados cobrindo CP1 e os fluxos novos da CP2 |
| LLM | `POST /api/v1/insights` via Gemini API, com timeout e fallback local |
| Importação inteligente | Prévia PDF/CSV/OFX/QFX, classificação PF/PJ, revisão humana e deduplicação |
| Extratos públicos | PDF combinado e três páginas individuais em `CP2/` |

## Critérios de aceite

- O usuário consegue se cadastrar, autenticar e navegar pelo frontend.
- O dashboard apresenta apenas dados do usuário autenticado no período escolhido.
- Receitas, despesas, resultado, saldo e taxa de economia são calculados pela API.
- Contas são listadas sem uma consulta adicional de saldo por conta.
- Nomes de contas, categorias e metas, além de e-mails, são únicos sem diferenciar maiúsculas e minúsculas.
- A aplicação continua útil sem `GEMINI_API_KEY`; nesse caso, informa que utilizou análise local.
- API, PostgreSQL e frontend sobem com `docker compose up --build`.

## Validação realizada

- `pytest -q`: **12 testes aprovados**.
- `docker compose exec api pytest -q`: suíte disponível dentro da imagem Docker.
- `node --check frontend/app.js`: JavaScript válido.
- `docker compose config --quiet`: configuração válida.
- Builds Docker da API e do frontend concluídos.
- PostgreSQL inicializado com Alembic em `0003 (head)`.
- Smoke test em containers: saúde `UP`, frontend HTTP `200`, cadastro, login e resumo aprovados.
- Gemini validado em chamada real para insights e classificação de extrato em PESSOAL/NEGÓCIO.
- [`Extratos públicos para teste.pdf`](<Extratos públicos para teste.pdf>) validado por leitura multimodal: 16 lançamentos extraídos na prévia, sem persistência automática.

> A conferência visual interativa deve ser repetida em um navegador antes da apresentação final, pois o ambiente de automação usado na implementação não disponibilizou uma superfície de navegador controlável.
