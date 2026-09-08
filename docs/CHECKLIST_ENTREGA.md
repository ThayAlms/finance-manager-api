# Checklist da CP1

| Entrega | Estado | Evidência |
|---|---|---|
| Definição do problema e escopo | Concluída | `docs/escopo.md` |
| Regras de negócio | Concluída | `docs/regras-de-negocio.md` (RN01 a RN17) e os serviços |
| Arquitetura do backend | Concluída | Camadas router, service, repository, schema e model em `app/` |
| API REST funcional | Concluída | 26 operações em `/api/v1`, com CRUD completo e `/resumo` |
| Banco de dados | Concluída | PostgreSQL 16, SQLAlchemy, Alembic e Compose |
| Documentação Swagger | Concluída | `/docs` e `/openapi.json`, com descrição e exemplos em todos os endpoints |
| GitHub e README | Concluída | `README.md` com instalação, variáveis, endpoints e arquitetura |
| Trello | Concluída | Link no `README.md`, seção **Planejamento** |
| Testes automatizados | Concluída | `pytest -q`, com CI contra PostgreSQL real a cada push |

## O que mudou depois da revisão do CP1

| Item | O que faltava | Situação |
|---|---|---|
| `GET /resumo` | Prometido em `docs/escopo.md` e inexistente no código | Implementado, com quebra PESSOAL/NEGOCIO |
| Filtros de transação | O escopo prometia `tipo` e `natureza`; só havia período | Implementados e acumulativos |
| Swagger | 12 operações sem `summary`, nenhuma com `description`, zero exemplos | Todas documentadas; 17 schemas com exemplo |
| README | Sem instalação, variáveis de ambiente, endpoints, arquitetura e Trello | Todas as seções incluídas |
