# Regras de negócio — CaixaLivre

O modelo prioriza o controle financeiro de autônomos, freelancers e MEIs. Violações de formato retornam `400`, autenticação retorna `401`, permissão retorna `403`, recursos não encontrados retornam `404`, conflitos de estado retornam `409` e regras semânticas retornam `422`.

| ID | Regra | Garantia |
|---|---|---|
| RN01 | Cada conta, categoria personalizada, transação e meta pertence ao usuário autenticado. Recursos alheios são tratados como inexistentes. | JWT e consultas filtradas pelo proprietário. |
| RN02 | O e-mail é único e normalizado em letras minúsculas. | Serviço e `UNIQUE` no PostgreSQL. |
| RN03 | A senha nunca é armazenada ou devolvida em texto. | Hash BCrypt e schemas sem senha. |
| RN04 | O valor de uma transação deve ser positivo. | Pydantic e `CHECK (valor > 0)`. |
| RN05 | O tipo da transação deve ser igual ao tipo da categoria. | Serviço de transações. |
| RN06 | Conta e categoria usadas na transação devem ser acessíveis ao usuário autenticado. | Serviços filtram pelo proprietário; categorias de sistema são compartilhadas. |
| RN07 | O saldo atual é calculado: saldo inicial + receitas − despesas. | Agregação no repositório; não existe coluna mutável de saldo atual. |
| RN08 | Categoria com transações não pode ser excluída. | Serviço e FK `RESTRICT`. |
| RN09 | Categorias de sistema são imutáveis pela API. | Operações de alteração e exclusão retornam `403`. |
| RN10 | Conta com transações não pode ser excluída. | Serviço e FK `RESTRICT`. |
| RN11 | O valor-alvo da meta é positivo e o valor atual não é negativo. | Pydantic e constraints do banco. |
| RN12 | Progresso, valor restante e situação atingida são calculados na resposta. | Serviço de metas. |
| RN13 | Não são aceitas transações futuras na CP1. | Serviço retorna `422`. |
| RN14 | Conta e transação possuem natureza `PESSOAL` ou `NEGOCIO`. | Enum obrigatório; transação herda a natureza da conta quando omitida. |
| RN15 | Nome e tipo da categoria são únicos por usuário. | Serviço e índice parcial único. |
| RN16 | Categorias padrão pertencem ao sistema e são visíveis para todos. | `usuario_id` nulo e carga inicial do Alembic. |
| RN17 | Valores monetários usam BRL com duas casas e `Decimal/NUMERIC`, nunca `float`. | Schemas Python e colunas `NUMERIC(14,2)`. |

## Restrições da CP1

- Apenas BRL;
- sem cartão de crédito, parcelamento, recorrência ou transferência entre contas;
- metas são atualizadas manualmente;
- transações futuras não representam contas a pagar nesta etapa.
