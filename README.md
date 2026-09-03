# FinAI — Finance Manager API

Backend REST para controle financeiro pessoal, desenvolvido em Java 21 e Spring Boot. O projeto permite administrar usuários, categorias, contas, receitas, despesas e metas financeiras.

## Entregas

| Requisito | Implementação |
|---|---|
| Regras de negócio | Serviços, validações e [documentação funcional](docs/REGRAS_DE_NEGOCIO.md) |
| Formato API | API REST/JSON versionada em `/api/v1` |
| Backend | Java 21, Spring Boot, Spring Web e arquitetura em camadas |
| GitHub com README | Repositório Git, este README e validação por GitHub Actions |
| Documentação | [Contrato da API](docs/API.md), [requisições de exemplo](docs/requests.http) e [checklist](docs/CHECKLIST_ENTREGA.md) |
| Swagger | Swagger UI e contrato OpenAPI 3 |
| Conexão com banco | PostgreSQL, Spring Data JPA, Flyway e Docker Compose |

## Integrantes

- Thainá Almeida Santos — RM 569110
- Vitor Barbosa Vitorino — RM 570475
- Silvio Dela Libera Neto — RM 572632

## Regras de negócio principais

- O e-mail do usuário é válido, único e normalizado em letras minúsculas.
- A senha possui de 8 a 72 caracteres e é armazenada como hash BCrypt.
- Categorias e contas pertencem a um único usuário e não podem ser duplicadas para ele.
- Usuário, conta e categoria de uma transação devem ser compatíveis.
- O tipo da transação deve ser igual ao tipo da categoria.
- Somente transações `COMPLETED` movimentam o saldo.
- Receitas concluídas creditam e despesas concluídas debitam a conta.
- Atualizar ou excluir uma transação concluída reverte seu efeito anterior.
- Recursos com dados financeiros vinculados não podem ser excluídos.
- O valor atual de uma meta não pode superar o valor-alvo.
- O prazo de uma meta não pode estar no passado.

Todas as regras e seus códigos estão em [REGRAS_DE_NEGOCIO.md](docs/REGRAS_DE_NEGOCIO.md).

## Arquitetura

```text
Cliente HTTP
    ↓
Controller → DTO e validação
    ↓
Service → regras de negócio
    ↓
Repository → Spring Data JPA
    ↓
PostgreSQL → schema versionado pelo Flyway
```

Entidades persistidas:

- `User`: proprietário dos dados;
- `Category`: classificação de receitas e despesas;
- `Account`: conta, carteira ou investimento e seu saldo;
- `FinancialTransaction`: receita ou despesa;
- `Goal`: meta financeira e progresso.

## Tecnologias

- Java 21;
- Spring Boot 3.3.5;
- Spring Web, Data JPA e Bean Validation;
- PostgreSQL 16;
- Flyway;
- Springdoc OpenAPI/Swagger;
- BCrypt;
- Maven;
- JUnit 5, MockMvc e H2 para testes;
- Docker e Docker Compose.

## Configuração

Pré-requisitos: Docker Desktop com Docker Compose ou JDK 21, Maven 3.9+ e PostgreSQL 16.

| Variável | Padrão | Finalidade |
|---|---|---|
| `DB_NAME` | `finai` | Nome do banco |
| `DB_HOST` | `localhost` | Servidor PostgreSQL |
| `DB_PORT` | `5432` | Porta PostgreSQL |
| `DB_USERNAME` | `finai` | Usuário do banco |
| `DB_PASSWORD` | `finai` | Senha do banco |
| `SERVER_PORT` | `8080` | Porta da API |

O arquivo `.env.example` contém valores apenas para desenvolvimento. Credenciais reais não devem ser enviadas ao GitHub.

## Execução

API e PostgreSQL com Docker:

```bash
docker compose up --build
```

Somente PostgreSQL com Docker e API pelo Maven:

```bash
docker compose up -d postgres
mvn spring-boot:run
```

A API ficará disponível em `http://localhost:8080`.

## Endpoints

| Método | Endpoint | Operação |
|---|---|---|
| `GET` | `/api/v1/users` | Listar usuários |
| `GET` | `/api/v1/users/{id}` | Consultar usuário |
| `POST` | `/api/v1/users` | Criar usuário |
| `PUT` | `/api/v1/users/{id}` | Atualizar usuário |
| `DELETE` | `/api/v1/users/{id}` | Excluir usuário |
| `GET` | `/api/v1/categories?userId={uuid}` | Listar categorias |
| `GET` | `/api/v1/categories/{id}` | Consultar categoria |
| `POST` | `/api/v1/categories` | Criar categoria |
| `PUT` | `/api/v1/categories/{id}` | Atualizar categoria |
| `DELETE` | `/api/v1/categories/{id}` | Excluir categoria |
| `GET` | `/api/v1/accounts?userId={uuid}` | Listar contas |
| `GET` | `/api/v1/accounts/{id}` | Consultar conta e saldo |
| `POST` | `/api/v1/accounts` | Criar conta |
| `PUT` | `/api/v1/accounts/{id}` | Atualizar conta |
| `DELETE` | `/api/v1/accounts/{id}` | Excluir conta |
| `GET` | `/api/v1/transactions?userId={uuid}&startDate={data}&endDate={data}` | Listar transações |
| `GET` | `/api/v1/transactions/{id}` | Consultar transação |
| `POST` | `/api/v1/transactions` | Criar transação |
| `PUT` | `/api/v1/transactions/{id}` | Atualizar e recalcular saldo |
| `DELETE` | `/api/v1/transactions/{id}` | Excluir e reverter saldo |
| `GET` | `/api/v1/goals?userId={uuid}` | Listar metas |
| `GET` | `/api/v1/goals/{id}` | Consultar meta |
| `POST` | `/api/v1/goals` | Criar meta |
| `PUT` | `/api/v1/goals/{id}` | Atualizar meta |
| `DELETE` | `/api/v1/goals/{id}` | Excluir meta |

## Swagger

Com a aplicação em execução:

- Swagger UI: [http://localhost:8080/swagger-ui.html](http://localhost:8080/swagger-ui.html)
- OpenAPI JSON: [http://localhost:8080/v3/api-docs](http://localhost:8080/v3/api-docs)

O Swagger documenta schemas, parâmetros, exemplos, respostas de sucesso e o formato padronizado dos erros `400`, `404`, `409` e `500`.

## Banco de dados

O PostgreSQL é configurado em `application.yml`. O Flyway cria e versiona as tabelas por meio de `src/main/resources/db/migration/V1__create_core_tables.sql`.

O schema contém chaves primárias UUID, chaves estrangeiras, índices, unicidade e validações monetárias.

## Testes

```bash
mvn clean verify
```

Os testes verificam inicialização, migração, regras financeiras, validações, erros e publicação do OpenAPI. O mesmo comando é executado pelo GitHub Actions.
