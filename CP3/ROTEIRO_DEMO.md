# Roteiro de apresentação e demonstração

Tempo sugerido: 8 a 10 minutos.

## 1. Problema e solução - 1 minuto

Apresentar o CaixaLivre e explicar a dor de autônomos, freelancers e MEIs que
misturam dinheiro pessoal e do negócio. Destacar que toda conta e transação tem
natureza PESSOAL ou NEGOCIO.

## 2. Arquitetura - 1 minuto

Mostrar frontend, FastAPI, PostgreSQL, Alembic e integração opcional com Gemini.
Explicar que a implantação pública entrega frontend e API no mesmo domínio e
mantém o banco privado.

## 3. Fluxo principal publicado - 3 minutos

1. Abrir a URL pública e `/health`.
2. Cadastrar um novo usuário e autenticar.
3. Criar uma conta de negócio com saldo inicial.
4. Registrar uma receita e uma despesa.
5. Mostrar o saldo calculado e o dashboard por natureza.
6. Tentar uma data futura para demonstrar erro tratado.
7. Se houver chave Gemini, importar um extrato público e revisar a prévia sem
   confirmar dados sensíveis.

## 4. Testes e falhas - 1 minuto

Executar `python -m pytest -q` ou exibir a execução do GitHub Actions. Apontar os
15 testes e abrir a matriz `docs/CENARIOS_TESTE.md`. Destacar isolamento entre
usuários, senha com BCrypt, duplicidade de extrato e fallback sem Gemini.

## 5. Docker e deploy - 1 minuto

Mostrar `Dockerfile`, `compose.yaml`, `Dockerfile.vercel` e `vercel.json`.
Executar `docker compose ps` e `curl http://localhost:8000/health`. Explicar a
região de São Paulo, o PostgreSQL Neon e as variáveis mantidas fora do Git.

## 6. Monetização - 1 minuto

Apresentar plano gratuito e Pro de R$ 19,90. No cenário com 500 cadastrados e 50
assinantes, a receita bruta simulada é R$ 995 e o resultado antes da mão de obra
é R$ 495,50. Explicar que os valores são premissas a validar.

## 7. Encerramento - 30 segundos

Mostrar repositório, quadro ágil e limitações. Informar que gateway de pagamento
e teste com cliente ficaram fora do escopo obrigatório.

## Plano de contingência

- Manter a aplicação local pronta via Compose caso o provedor esteja despertando.
- Levar o resultado dos testes e logs sem dados sensíveis.
- Usar o extrato público de demonstração, nunca um extrato bancário real.
- Não afirmar que a IA respondeu ao vivo se estiver usando fallback local.
