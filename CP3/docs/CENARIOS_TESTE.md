# Cenários e resultados de teste

**Execução registrada:** 20/10/2026

**Ambiente:** Windows 11, Python 3.12, suíte local com SQLite em memória
**Comando:** `python -m pytest -q`

## Resultado automatizado

```text
...............                                                          [100%]
15 passed
```

O aviso de depreciação emitido pela combinação atual de FastAPI/TestClient e
HTTPX não representa falha funcional. O pipeline repete a suíte com PostgreSQL
16, executa as migrações e constrói as duas imagens Docker.

## Matriz de cenários

| ID | Fluxo e tipo | Operação | Resultado esperado | Resultado obtido | Evidência automatizada |
|---|---|---|---|---|---|
| CT-01 | Cadastro e login, sucesso | Cadastrar e-mail em caixa alta, autenticar e consultar perfil protegido | Usuário `201`, e-mail normalizado, token válido e perfil `200` sem senha | Conforme esperado | `test_registration_login_and_protected_profile` |
| CT-02 | Senha, segurança | Consultar diretamente o registro criado | Banco contém hash BCrypt, nunca a senha original | Conforme esperado | `test_password_is_stored_only_as_bcrypt_hash` |
| CT-03 | Fluxo financeiro, integração | Criar conta PJ, lançar receita de R$ 500 e despesa de R$ 200 sobre saldo inicial de R$ 1.000 | Saldo calculado em R$ 1.300; exclusão da conta bloqueada enquanto houver movimentos | Conforme esperado | `test_financial_workflow_and_calculated_balance` |
| CT-04 | Dados inválidos, erro | Enviar data futura, valor negativo e categoria incompatível | API rejeita com HTTP 422 e informa o campo inválido | Conforme esperado | `test_transaction_rules` |
| CT-05 | Autorização, erro | Usuário B tenta consultar conta do usuário A | API responde 404 e não revela o recurso | Conforme esperado | `test_user_cannot_access_another_users_account` |
| CT-06 | Dashboard e filtros, integração | Criar receita e despesa e consultar resumo/listagem filtrada | Totais, resultado, saldo, taxa de economia e paginação coerentes | Conforme esperado | `test_dashboard_summary_filters_and_pagination` |
| CT-07 | Extrato CSV, integração | Gerar prévia, revisar, confirmar e repetir o mesmo arquivo | Duas transações importadas na primeira execução e duplicatas detectadas na segunda | Conforme esperado | `test_statement_preview_confirmation_and_duplicate_detection` |
| CT-08 | LLM, integração simulada | Enviar PDF em Base64 com cliente HTTP do Gemini substituído por resposta controlada | Documento segue como `application/pdf`; lançamento estruturado retorna com modelo identificado | Conforme esperado | `test_pdf_statement_is_sent_to_gemini_as_multimodal_document` |
| CT-09 | Indisponibilidade externa | Solicitar insight sem chave Gemini | API responde `200` com análise local e aviso explícito | Conforme esperado | `test_insight_uses_safe_local_fallback_without_api_key` |
| CT-10 | Publicação unificada | Acessar `/` pela mesma aplicação FastAPI usada no deploy | HTML do CaixaLivre responde `200`; `/api/v1` permanece funcional | Conforme esperado | `test_frontend_is_served_by_production_api_image` |
| CT-11 | Compatibilidade de deploy | Carregar URL PostgreSQL fornecida pelo provedor | Configuração seleciona explicitamente o driver `psycopg` instalado | Conforme esperado | `test_cloud_postgres_url_uses_installed_psycopg_driver` |

## Integrações verificadas

- **Frontend e API:** o frontend usa caminhos relativos `/api/v1`, e a imagem de
  produção entrega ambos no mesmo domínio.
- **API e banco:** `/health` executa `SELECT 1`; o CI aplica `alembic upgrade head`
  em PostgreSQL 16 antes dos testes.
- **Gemini:** chamadas externas são simuladas nos testes para obter resultado
  determinístico. Sem chave, o insight usa fallback local; PDFs retornam erro
  controlado porque exigem leitura multimodal.

## Evidências e correções do CP3

| Achado | Correção | Validação |
|---|---|---|
| O frontend só era servido pelo contêiner Nginx local | A API passou a servir a SPA no deploy de serviço único | CT-10 |
| A URL PostgreSQL do provedor não informa o driver SQLAlchemy | Normalização para `postgresql+psycopg://` | CT-11 |
| O servidor usava porta fixa `8000` | Dockerfile agora respeita `PORT` e mantém `8000` como padrão | build da imagem e health check |
| O CP3 não tinha documentação verificável | Matriz de cenários, deploy, monetização, quadro e roteiro adicionados | auditoria em `CP3/README.md` |

## Evidência de contêiner

Em 20/10/2026, o Docker Compose construiu as imagens, iniciou PostgreSQL, API e
frontend, aplicou as migrações e executou os 15 testes dentro do contêiner. A API
e o proxy do frontend retornaram `{"status":"UP"}`; as páginas em `:8000/` e
`:3000/` responderam HTTP 200. O log resumido está em
[`../evidencias/docker-compose.txt`](../evidencias/docker-compose.txt).
