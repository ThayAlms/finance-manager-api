# Decisões da integração

Foram comparadas a base CaixaLivre da branch `feature/python-vitor` e a implementação anterior FinAI. O CaixaLivre foi mantido como modelo oficial; recursos anteriores foram incorporados apenas quando compatíveis.

| Tema | Decisão final | Motivo |
|---|---|---|
| Produto | CaixaLivre para autônomos, freelancers e MEIs | Preserva o recorte e a proposta do projeto do Vitor. |
| Arquitetura | Módulos `routers`, `services`, `repositories`, `models` e `schemas` | Preserva a estrutura do Vitor e evita um arquivo monolítico. |
| Propriedade | Usuário obtido do JWT | Evita aceitar `userId` manipulável na requisição. |
| Saldo | Calculado a partir das transações | Evita divergência entre saldo armazenado e extrato. |
| Transação | Sem `usuario_id` redundante | O proprietário já é definido pela conta; mantém 3FN. |
| Natureza | `PESSOAL` ou `NEGOCIO` | Sustenta o diferencial do CaixaLivre. |
| Categorias | Padrões do sistema mais personalizadas | Facilita o primeiro uso sem perder personalização. |
| Banco | Alembic, constraints e seed | Garante schema reproduzível e versionado. |
| API | CRUD REST, erros padronizados e Swagger | Incorpora a completude técnica da implementação anterior. |
| Qualidade | Testes e CI | Registra e verifica automaticamente as regras principais. |

Não foram mantidos nomes, endpoints ou regras do FinAI que conflitavam com o domínio CaixaLivre.
