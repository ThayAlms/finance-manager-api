# Validação final antes do envio

## Automação

- [x] `python -m pytest -q` executado em 20/10/2026.
- [ ] GitHub Actions verde na branch final.
- [x] `docker compose build` concluído com Docker Desktop ativo em 20/10/2026.
- [x] `docker compose up -d` com `postgres`, `api` e `frontend` em execução.
- [x] `curl http://localhost:8000/health` retorna `{"status":"UP"}`.
- [x] `Dockerfile.vercel` construído e validado localmente com `/` e `/health` HTTP 200.

## Deploy

- [ ] Projeto importado na Vercel a partir do repositório GitHub.
- [ ] PostgreSQL Neon conectado pelo Marketplace da Vercel.
- [ ] Variáveis de produção configuradas sem expor seus valores.
- [ ] URL pública inserida em `CP3/docs/DEPLOY.md` e nos READMEs.
- [ ] `/`, `/health` e `/docs` acessíveis na URL pública.
- [ ] Cadastro, login, conta e transações demonstrados no ambiente publicado.
- [ ] Print do painel sem segredos salvo em `CP3/evidencias/`.

## Apresentação

- [ ] PPTX aberto no PowerPoint e fontes/layout conferidos.
- [ ] Integrantes e RMs confirmados.
- [ ] Link do repositório e endereço do deploy testados.
- [ ] Roteiro ensaiado em até 10 minutos.
- [ ] Extrato usado na demonstração não contém dados pessoais reais.

## Empacotamento

- [x] Excluir caches e arquivos locais do pacote de entrega.
- [x] Não incluir `.env`, chaves, tokens ou credenciais.
- [x] Gerar `CP3_CAIXALIVRE.zip` com conteúdo selecionado.
- [x] Abrir o ZIP e conferir código, testes, Dockerfile, Compose, docs e evidências.
