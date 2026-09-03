# FinAI - Finance Manager API

API REST para controle financeiro pessoal, desenvolvida em Java 21 e Spring Boot. O sistema permite administrar usuários, categorias, contas, receitas, despesas e metas financeiras.

## Visao geral

Cada recurso financeiro pertence a um usuário por meio de `userId`. As consultas de contas, categorias, transações e metas são filtradas pelo usuário informado, e as regras de negócio impedem relacionamentos entre dados de usuários diferentes.

O projeto está preparado para desenvolvimento local com Docker Compose:

- PostgreSQL 16 para persistência dos dados;
- Flyway para criar e versionar o schema;
- API Spring Boot executada em um container Java 21;
- volume Docker para manter os dados do banco entre reinícios.

> A versão atual usa `userId` nas requisições para identificar o proprietário dos dados. Autenticação com login, token e autorização por usuário ainda não faz parte desta entrega.

## Entregas

| Requisito | Implementação |
|---|---|
| Regras de negócio | Serviços, validações e [documentação funcional](docs/REGRAS_DE_NEGOCIO.md) |
| Formato API | API REST/JSON versionada em `/api/v1` |
| Backend | Java 21, Spring Boot, Spring Web e arquitetura em camadas |
| Documentação | [Contrato da API](docs/API.md), [requisições de exemplo](docs/requests.http) e [checklist](docs/CHECKLIST_ENTREGA.md) |
| Swagger | Swagger UI e contrato OpenAPI 3 |
| Conexão com banco | PostgreSQL, Spring Data JPA, Flyway e Docker Compose |

## Integrantes

- Thainá Almeida Santos — RM 569110
- Vitor Barbosa Vitorino — RM 570475
- Silvio Dela Libera Neto — RM 572632

## Estrutura

```text
src/main/java/br/com/finai/
    controller/  endpoints HTTP e documentação OpenAPI
    domain/      entidades e enums do domínio
    dto/         objetos de entrada e saída da API
    exception/   erros de negócio e tratamento global
    repository/  acesso aos dados com Spring Data JPA
    service/     regras de negócio e transações
src/main/resources/
    application.yml
    db/migration/  scripts versionados do Flyway
docs/          contrato, regras e materiais da entrega
```

## Regras de negócio

As regras funcionais, seus códigos e respostas HTTP estão centralizados em [REGRAS_DE_NEGOCIO.md](docs/REGRAS_DE_NEGOCIO.md).

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

Pré-requisitos: Docker Desktop com Docker Compose. Para executar a API fora do Docker, também são necessários JDK 21, Maven 3.9+ e PostgreSQL 16.

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

Para verificar os containers:

```bash
docker compose ps
```

Para acompanhar os logs da API:

```bash
docker compose logs -f api
```

Para parar os serviços sem remover os dados persistidos:

```bash
docker compose down
```

O `Dockerfile` usa uma etapa Maven para compilar o `.jar` e uma imagem final menor com Java 21 JRE. O `compose.yaml` conecta a API ao PostgreSQL pelo nome do serviço `postgres`.

## API

Os recursos disponíveis são usuários, categorias, contas, transações e metas, todos versionados em `/api/v1`. O contrato completo, a sequência recomendada de testes e o formato de erros estão em [docs/API.md](docs/API.md). Requisições prontas estão em [docs/requests.http](docs/requests.http).

## Swagger

Com a aplicação em execução:

- Swagger UI: [http://localhost:8080/swagger-ui.html](http://localhost:8080/swagger-ui.html)
- OpenAPI JSON: [http://localhost:8080/v3/api-docs](http://localhost:8080/v3/api-docs)

O Swagger documenta schemas, parâmetros, exemplos, respostas de sucesso e o formato padronizado dos erros `400`, `404`, `409` e `500`.

## Banco de dados

O PostgreSQL é configurado em `application.yml`. O Flyway cria e versiona as tabelas por meio de `src/main/resources/db/migration/V1__create_core_tables.sql`.

O schema contém chaves primárias UUID, chaves estrangeiras, índices, unicidade e validações monetárias.

Quando a API roda no Docker, a conexão usa `DB_HOST=postgres`. Quando a API roda diretamente na máquina, o banco deve ser acessado com `DB_HOST=localhost`.

## Testes

```bash
mvn clean verify
```

Os testes verificam inicialização, migração, regras financeiras, validações, erros e publicação do OpenAPI. O mesmo comando é executado pelo GitHub Actions.
