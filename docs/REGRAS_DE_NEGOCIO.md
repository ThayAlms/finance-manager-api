# Regras de negócio — FinAI

Este documento é a referência funcional da versão `v1` da API. As regras são aplicadas na camada de serviço e, quando possível, também por validações de entrada e restrições do banco.

## Usuários

| ID | Regra | Comportamento da API |
|---|---|---|
| RN-01 | O e-mail deve ter formato válido e ser único, sem diferenciar maiúsculas de minúsculas. | Retorna `400` para formato inválido e `409` para duplicidade. |
| RN-02 | A senha deve ter entre 8 e 72 caracteres. | Retorna `400` quando o tamanho é inválido. |
| RN-03 | Senhas nunca são persistidas em texto puro. | A camada de serviço gera um hash BCrypt antes da gravação. |
| RN-04 | Usuários com categorias, contas, transações ou metas vinculadas não podem ser excluídos. | Retorna `409`. |

## Categorias e contas

| ID | Regra | Comportamento da API |
|---|---|---|
| RN-05 | A categoria pertence a um usuário e é do tipo `INCOME` ou `EXPENSE`. | Tipo e proprietário são obrigatórios. |
| RN-06 | Nome e tipo da categoria formam uma combinação única por usuário. | Retorna `409` para duplicidade. |
| RN-07 | O nome da conta é único por usuário. | Retorna `409` para duplicidade. |
| RN-08 | O saldo inicial de uma conta não pode ser negativo. | Retorna `400`. |
| RN-09 | O saldo não pode ser editado diretamente após a criação da conta. | O contrato de atualização aceita somente nome e tipo. |
| RN-10 | Contas e categorias com transações não podem ser excluídas. | Retorna `409`. |

## Transações

| ID | Regra | Comportamento da API |
|---|---|---|
| RN-11 | O valor deve ser positivo e representado com precisão decimal. | Retorna `400`; valores monetários usam `BigDecimal`. |
| RN-12 | Usuário, conta e categoria da transação devem ser os mesmos proprietários. | Retorna `409` quando os vínculos são incompatíveis. |
| RN-13 | O tipo da categoria deve ser igual ao tipo da transação. | Retorna `409`. |
| RN-14 | Somente transações `COMPLETED` afetam o saldo. | `PENDING` e `CANCELLED` não movimentam a conta. |
| RN-15 | Receitas concluídas creditam e despesas concluídas debitam o saldo. | Alteração automática e atômica na mesma transação de banco. |
| RN-16 | Ao alterar ou excluir uma transação concluída, o efeito anterior é revertido. | O saldo é recalculado dentro da mesma transação de banco. |
| RN-17 | Uma transação não pode ser transferida para outro usuário na atualização. | Retorna `409`. |
| RN-18 | O início de um filtro por período não pode ser posterior ao fim. | Retorna `409`. |

## Metas

| ID | Regra | Comportamento da API |
|---|---|---|
| RN-19 | O valor-alvo deve ser positivo e o valor atual não pode ser negativo. | Retorna `400`. |
| RN-20 | O valor atual não pode superar o valor-alvo. | Retorna `409`. |
| RN-21 | O prazo, quando informado, não pode estar no passado. | Retorna `409`. |
| RN-22 | Uma meta não pode ser transferida para outro usuário na atualização. | Retorna `409`. |
| RN-23 | Progresso e valor restante são calculados pela API. | A resposta limita o progresso a `100%` e o restante a zero. |

## Códigos de erro

- `400 Bad Request`: contrato JSON, parâmetro ou validação de entrada inválida;
- `404 Not Found`: identificador não encontrado;
- `409 Conflict`: regra de negócio, duplicidade ou integridade violada;
- `500 Internal Server Error`: erro inesperado sem exposição de detalhes internos.

Todos os erros seguem o objeto `ApiError`, com data/hora, status, mensagem, caminho e erros de campo quando aplicável.
