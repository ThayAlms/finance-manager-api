# Auditoria do Checkpoint 3

**Data:** 20/10/2026
**Referência:** enunciado de testes, deploy, containerização e monetização

## Cobertura do barema

| Critério | Valor | Evidência da entrega | Estado |
|---|---:|---|---|
| Testes funcionais e de integração | 1,5 | 15 testes e 11 cenários em `docs/CENARIOS_TESTE.md` | atendido |
| Evidências e tratamento de falhas | 1,0 | resultados esperados/obtidos, erros 422/404/409, correções e log Docker | atendido |
| Deploy e funcionamento | 2,0 | `Dockerfile.vercel`, `vercel.json`, teste em `evidencias/vercel-container.txt` e guia `docs/DEPLOY.md` | implementação pronta; URL pública pendente |
| Containerização com Docker | 2,0 | Dockerfiles, Compose, três serviços ativos, health `UP` e testes na imagem | atendido |
| Proposta de monetização | 1,5 | público, freemium, preço, faturamento, custos, ponto de equilíbrio e riscos | atendido |
| Documentação, GitHub e organização ágil | 1,0 | READMEs, documentação técnica, GitHub, Trello e quadro versionado | atendido |
| Apresentação e demonstração final | 1,0 | PPTX de 9 slides e roteiro de 8 a 10 minutos | atendido |

## Requisitos obrigatórios conferidos

- mínimo de cinco cenários: 11 documentados;
- sucesso e erro: ambos presentes;
- mínimo de dois testes automatizados: 15 aprovados;
- integração: frontend/API, API/PostgreSQL e Gemini simulado;
- evidências: log de execução, matriz e correções;
- Dockerfile funcional e Compose para múltiplos serviços;
- configurações por variáveis de ambiente;
- ausência de segredos no pacote;
- público, modelo de receita, preço, custos e viabilidade;
- integrantes e RMs no README;
- links do GitHub e Trello;
- arquitetura, instalação, testes, deploy e Docker documentados;
- apresentação e roteiro de demonstração preparados.

## Única pendência que depende da equipe

O repositório contém toda a configuração de publicação, mas uma URL pública real
só existe depois que um integrante conecta o GitHub à conta da Vercel, adiciona
um PostgreSQL pelo Marketplace e confirma o deploy. Após publicar, substituir
`PENDENTE_APOS_PUBLICACAO_NA_VERCEL` nos dois arquivos indicados pelo guia de
deploy e registrar um print sem segredos.

Sem essa etapa externa, o critério de deploy não pode ser apresentado como
concluído. A entrega mantém a pendência explícita para não usar evidência falsa.
