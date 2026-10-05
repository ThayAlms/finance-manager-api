# Evidências de validação do CP2

**Última execução:** 05/10/2026

**Branch:** `checkpoint-2`

## Build e execução

| Verificação | Resultado |
|---|---|
| `docker compose up -d --build api frontend` | imagens reconstruídas e containers iniciados |
| Migração no startup | Alembic em `0003 (head)` |
| Frontend | disponível em `http://localhost:3000` |
| API e Swagger | disponíveis nas portas documentadas |

## Testes automatizados

Comando executado dentro da imagem distribuída:

```bash
docker compose exec api pytest -q
```

Resultado:

```text
13 passed, 1 warning
```

O warning vem da compatibilidade futura entre TestClient e HTTPX; não representa
falha funcional. A suíte cobre autenticação, hash BCrypt, autorização, CRUD, dashboard,
filtros, normalização, importação e integração mockada com Gemini.

## LLM e importação

- Em 04/10/2026, `Extratos públicos para teste.pdf` produziu uma prévia real com
  16 lançamentos usando `gemini-3.8-flash`.
- A prévia apresentou créditos e débitos de R$ 1.641.717,06.
- Nenhum lançamento foi persistido durante essa validação.
- Em 05/10/2026, o provedor/chave ficou indisponível: PDFs retornaram erro `422`
  tratado e o endpoint de insights respondeu com análise local.
- Os testes automatizados não dependem da disponibilidade externa do Gemini.

## Segurança verificada

- chave do Gemini ausente dos arquivos rastreados;
- `.env` ignorado pelo Git;
- PDF exige confirmação antes do envio;
- prévia não grava conta nem transações;
- senha, hash, JWT e e-mail não são enviados ao modelo;
- deduplicação protegida por índice único no banco.

## Validação manual ainda necessária

O grupo deve executar e marcar a checklist visual do
[`GUIA_TESTE_PROFESSOR.md`](GUIA_TESTE_PROFESSOR.md) em desktop e celular antes
da banca. Também deve anexar o link/captura do Trello ou Notion e criar o arquivo
final de slides a partir do roteiro fornecido.
