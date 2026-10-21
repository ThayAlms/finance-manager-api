# Quadro ágil do CP3

Este arquivo funciona como quadro Kanban versionado e auditável no próprio Git.
Cada alteração fica registrada no histórico do repositório.

## Concluído

| Item | Responsável sugerido | Evidência |
|---|---|---|
| Mapear barema do CP3 | equipe | `CP3/README.md` |
| Executar testes automatizados | equipe | `docs/CENARIOS_TESTE.md` |
| Servir frontend e API na mesma imagem de produção | backend | `Dockerfile`, `app/main.py` |
| Aceitar URL PostgreSQL do provedor | backend | `app/core/config.py` |
| Configurar deploy na Vercel | DevOps | `Dockerfile.vercel`, `vercel.json` |
| Documentar monetização | produto | `docs/MONETIZACAO.md` |
| Preparar roteiro e apresentação | equipe | `ROTEIRO_DEMO.md`, `Apresentacao_CP3_CaixaLivre.pptx` |

## Em validação

| Item | Responsável sugerido | Critério de aceite |
|---|---|---|
| Executar Compose com Docker Desktop ativo | DevOps | três serviços saudáveis e `/health` retornando `UP` |
| QA visual desktop e celular | frontend | fluxo principal sem cortes ou erros visuais |
| Publicar projeto na Vercel | DevOps | URL pública acessível e health check aprovado |

## Pendente externo

| Item | Responsável sugerido | Dependência |
|---|---|---|
| Inserir URL pública no README | equipe | deploy concluído na Vercel |
| Anexar captura/log do contêiner | equipe | Docker Desktop ativo |
| Gravar vídeo opcional | equipe | deploy público e apresentação ensaiada |
| Teste com cliente opcional | produto | disponibilidade de potencial usuário |

## Definição de pronto

Uma tarefa só passa para concluída quando possui arquivo, log, teste ou URL que
permita ao professor reproduzir a afirmação. Campos pendentes permanecem
explícitos para evitar evidência fictícia na entrega.
