# Plano para atualização do Trello ou Notion

O enunciado exige evidência de uma ferramenta externa. Este arquivo organiza o
conteúdo que deve ser copiado para o quadro do grupo; ele **não substitui** o
link ou a captura do Trello/Notion na entrega.

## Colunas sugeridas

- Backlog
- Em andamento
- Em revisão
- Concluído

## Cartões concluídos

| Cartão | Evidência no repositório |
|---|---|
| Consolidar autenticação JWT | `app/core/security.py`, testes de autenticação |
| Padronizar validações e erros | `app/core/errors.py`, schemas Pydantic |
| Criar frontend integrado | `frontend/` |
| Criar dashboard financeiro | `GET /api/v1/resumo` e tela Visão geral |
| Otimizar saldo das contas | consulta agregada em `app/repositories/account.py` |
| Adicionar filtros e paginação | `GET /api/v1/transacoes` |
| Revisar banco e índices | migrações `0002` e `0003` |
| Criar testes automatizados | `tests/`, 12 testes aprovados |
| Integrar insights com Gemini | `POST /api/v1/insights` |
| Importar extratos com IA | `/extratos/preview` e `/extratos/confirmar` |
| Atualizar Swagger e documentação | README, `docs/` e `CP2/` |

## Evidência obrigatória antes da entrega

1. Criar ou atualizar o quadro externo.
2. Marcar os cartões concluídos e atribuir responsáveis.
3. Registrar a data de conclusão.
4. Adicionar o link público ou uma captura em `CP2/README.md`.
5. Abrir o quadro durante a apresentação.
