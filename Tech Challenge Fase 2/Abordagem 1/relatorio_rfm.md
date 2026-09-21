# 📈 Relatório de Segmentação RFM (Abordagem 1)

> **Data de Geração:** 2026-07-20 19:07:23

> **Base Total de Clientes Analisados:** 96,096 compradores únicos

> **GMV Abrangido:** R$ 13,591,643.70


## 1. Contexto do Negócio
A análise de RFM (Recency, Frequency, Monetary) é uma técnica chave para segmentação de base de clientes.
No e-commerce brasileiro (Olist), observamos uma particularidade marcante:
**A taxa de recompra é extremamente baixa (aprox. 3%).** Isso significa que a esmagadora maioria
dos clientes possui `Frequencia = 1`. Por esse motivo, a métrica de frequência é pontuada de forma
customizada para destacar a minoria que compra recorrentemente.

---

## 2. Estatísticas Gerais dos Segmentos RFM

| Segmento | Clientes | % Clientes | Recência Média | Freq. Média | Monetário Médio | Receita Total | % Receita |
|---|---:|---:|---:|---:|---:|---:|---:|
| **Novos Promissores** | 22,451 | 23.4% | 141.8 dias | 1.00 | R$ 207.92 | R$ 4,667,943.76 | 34.3% |
| **Hibernando** | 21,585 | 22.5% | 445.8 dias | 1.00 | R$ 212.12 | R$ 4,578,613.63 | 33.7% |
| **Prestes a Dormir** | 18,414 | 19.2% | 271.2 dias | 1.00 | R$ 129.27 | R$ 2,380,299.11 | 17.5% |
| **Perdidos** | 15,791 | 16.4% | 447.5 dias | 1.00 | R$ 38.59 | R$ 609,309.44 | 4.5% |
| **Novos Clientes** | 14,858 | 15.5% | 139.5 dias | 1.00 | R$ 38.81 | R$ 576,655.79 | 4.2% |
| **Fiéis** | 1,624 | 1.7% | 184.4 dias | 2.04 | R$ 271.71 | R$ 441,249.23 | 3.2% |
| **Em Risco de Churn** | 1,054 | 1.1% | 433.4 dias | 2.08 | R$ 251.09 | R$ 264,648.51 | 1.9% |
| **Diversos / Outros** | 134 | 0.1% | 129.1 dias | 2.02 | R$ 48.60 | R$ 6,512.59 | 0.0% |
| **Campeões** | 130 | 0.1% | 142.6 dias | 3.52 | R$ 489.53 | R$ 63,638.71 | 0.5% |
| **Atenção Necessária** | 55 | 0.1% | 265.9 dias | 2.02 | R$ 50.42 | R$ 2,772.93 | 0.0% |

---

## 3. Principais Insights e Oportunidades Estratégicas

### 💥 A Dominância do Segmento 'Perdidos'
O maior segmento na Olist é o de **Perdidos**, representando **16.4%** da base. São clientes que compraram uma única vez há muito tempo (média de **447.5 dias** atrás) e gastaram pouco. Isso confirma o grande desafio de atração de leads sem fidelização posterior na plataforma.

### 🎯 A Oportunidade em 'Hibernando'
O segmento **Hibernando** representa **22.5%** dos clientes, mas responde por **33.7%** do total gasto. São clientes de alto valor monetário (gasto médio de **R$ 212.12**) que não realizam compras há bastante tempo. Reativar essa parcela da base via e-mail marketing personalizado ou ofertas exclusivas trará um retorno imediato de receita.

### 🏆 Os Poucos 'Campeões' & 'Fiéis'
Devido à baixíssima recompra estrutural do modelo de marketplace no período (2016-2018), os clientes **Campeões** e **Fiéis** juntos representam menos de 1.5% da base total de compradores, embora possuam um ticket médio e frequência de compra muito superiores aos demais.

---

## 4. Recomendações para a IA Agêntica (Seller Success & Growth Agent)
- **Reter Novos Clientes:** O agente deve disparar alertas automáticos ou convites de engajamento para a base de **Novos Promissores** e **Novos Clientes** nas primeiras semanas pós-entrega, oferecendo cupons para incentivar a segunda compra.
- **Campanhas de Reativação:** Desenhar e-mails dinâmicos voltados ao segmento **Hibernando**, utilizando as categorias mais compradas por eles como base para recomendação inteligente.
- **Ações com Sellers Locais:** Como frete alto e atraso geram detratores, o agente de crescimento de sellers deve orientar os lojistas a manter estoque mais próximo dos clusters de clientes que mais compram do segmento 'Novos Clientes' para garantir entregas mais baratas e ágeis.

---
## 5. Visualizações
- O gráfico da distribuição percentual e absoluta dos segmentos está disponível em: `distribuicao_segmentos_rfm.png`.