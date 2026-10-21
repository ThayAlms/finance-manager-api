# Proposta de monetização

## Público e problema

O CaixaLivre atende autônomos, freelancers e MEIs que misturam finanças pessoais
e do negócio. O produto organiza contas, transações, metas e extratos com essa
separação explícita, reduzindo o esforço de entender quanto o negócio realmente
gerou e quanto a pessoa pode reservar.

## Modelo de receita

O modelo proposto é **freemium com assinatura mensal**. A versão gratuita cria
o hábito e reduz a barreira de entrada. O plano Pro monetiza automação e análise,
que concentram custo variável e maior valor percebido.

| Recurso | Gratuito | Pro - R$ 19,90/mês |
|---|---:|---:|
| Contas, categorias e lançamentos manuais | sim | sim |
| Dashboard pessoal e negócio | sim | sim |
| Metas financeiras | até 2 | ilimitadas |
| Importação CSV/OFX | 1 arquivo/mês | ilimitada sob uso justo |
| Leitura de PDF e insights com IA | não | até 20 análises/mês |
| Exportação e histórico ampliado | não | sim |

O limite de IA controla custo e permite oferecer pacotes adicionais no futuro.
Não é necessário implementar cobrança no Checkpoint 3.

## Simulação mensal

Premissas de um estágio inicial:

- 500 usuários cadastrados;
- 10% de conversão para o plano Pro, ou 50 assinantes;
- preço mensal de R$ 19,90;
- impostos e taxas de pagamento estimados em 10% da receita;
- operação enxuta, com manutenção feita pelo grupo.

| Item | Cálculo | Valor mensal |
|---|---:|---:|
| Receita bruta | 50 x R$ 19,90 | R$ 995,00 |
| Hospedagem da aplicação | estimativa | R$ 130,00 |
| Banco de dados e backup | estimativa | R$ 100,00 |
| API Gemini | teto de uso | R$ 120,00 |
| Monitoramento e domínio | estimativa | R$ 50,00 |
| Taxas e impostos | 10% da receita | R$ 99,50 |
| Custo operacional total | soma dos custos | R$ 499,50 |
| Resultado antes da mão de obra | receita menos custos | **R$ 495,50** |

O ponto de equilíbrio operacional, com custo fixo de R$ 280, custo variável de
IA de R$ 120 e 10% de taxas, ocorre perto de **23 assinantes**:
`R$ 400 / (R$ 19,90 x 90%) = 22,33`.

## Viabilidade e premissas

No cenário proposto, a margem antes da remuneração da equipe fica próxima de
49,8%. A proposta permanece viável enquanto o uso de IA ficar dentro do limite
do plano e a conversão superar aproximadamente 4,6% dos 500 cadastrados. A
principal incerteza está no custo de LLM por documento e na retenção dos
assinantes. Antes de comercializar, o grupo deve medir uso real, revisar preços
de infraestrutura e incluir suporte, LGPD, contabilidade e remuneração da equipe
em um demonstrativo completo.

## Próximos testes de negócio

1. Entrevistar ao menos cinco autônomos ou MEIs e registrar a frequência de uso.
2. Medir quantos extratos e insights um usuário Pro consome por mês.
3. Validar disposição a pagar entre R$ 14,90 e R$ 24,90.
4. Acompanhar conversão, cancelamento e custo de IA por assinante.
