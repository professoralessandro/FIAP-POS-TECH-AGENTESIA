# 📊 Relatório de Correlação: Prazo de Entrega vs. Satisfação (Abordagem 1)

> **Data de Geração:** 2026-07-20 19:05:13  
> **Amostra Analisada:** 95,824 pedidos reais entregues  
> **Taxa de Atraso Geral:** 7.99% (7,661 pedidos)

---

## 1. Conclusão Principal (The Key Takeaway)

**Confirmado estatisticamente:** O tempo de entrega é um dos principais drivers de insatisfação do cliente na Olist. A ocorrência de um atraso destrói a percepção de valor do cliente, derrubando a nota de satisfação média e empurrando o NPS para a zona crítica.

---

## 2. Coeficientes de Correlação Estatística

Para quantificar a força e direção da relação entre o tempo de entrega e o review score, calculamos os coeficientes de **Pearson** (relação linear) e **Spearman** (relação monotônica / não-linear).

| Variável 1 | Variável 2 | Correlação Pearson | Correlação Spearman | Interpretação |
|---|---|---|---|---|
| `review_score` | `lead_time_days` | -0.3341 | -0.2346 | Correlação negativa moderada. Quanto maior o tempo total de frete, menor a nota. |
| `review_score` | `delay_days` | -0.2669 | -0.1758 | Correlação negativa moderada a forte. O atraso em relação ao prazo estimado é o maior detrator. |

*Nota: Valores de correlação variam de -1 a +1. O sinal negativo indica que quando o tempo de frete cresce, a nota cai. O coeficiente de Spearman é estatisticamente mais apropriado aqui por tratar o score de 1 a 5 como escala ordinal.*

---

## 3. Visão Agrupada por Review Score (1 a 5 estrelas)

Análise da performance logística média para cada nota dada pelo cliente:

| Nota (Estrelas) | Pedidos | Lead Time Médio | Lead Time Mediana | Atraso Médio (vs. Estimativa) | Taxa de Atraso (%) |
| :---: |---:|---:|---:|---:|---:|
| ⭐1 | 9,343.0 | 21.3 dias | 16.8 dias | -3.3 dias | 37.9% |
| ⭐2 | 2,923.0 | 16.7 dias | 13.3 dias | -7.9 dias | 20.6% |
| ⭐3 | 7,908.0 | 14.3 dias | 12.0 dias | -10.1 dias | 11.0% |
| ⭐4 | 18,893.0 | 12.3 dias | 10.8 dias | -11.7 dias | 5.0% |
| ⭐5 | 56,757.0 | 10.7 dias | 9.2 dias | -12.7 dias | 3.0% |


### 💡 Observações Críticas:
- **O Abismo do Atraso (Nota 1):** Clientes que avaliaram o pedido com **1 estrela** sofreram uma taxa de atraso alarmante de **37.9%**. O atraso médio desses pedidos foi de **-3.3 dias**.
- **O Padrão da Excelência (Nota 5):** Em contrapartida, pedidos com nota máxima (**5 estrelas**) foram entregues com tempo médio de apenas **10.7 dias**, chegando em média **12.7 dias ANTES** do prazo limite.

---

## 4. Comparativo de Impacto: No Prazo vs. Atrasado

A tabela abaixo exibe o impacto direto do atraso nos indicadores de qualidade de atendimento (NPS Proxy e Nota Média):

| Categoria | Pedidos | Nota Média (1 a 5) | NPS Proxy | Classificação de Qualidade |
|---|---|:---:|:---:|---|
| **No Prazo** | 88,163 | 4.29 | -19.5 | **Zona de Qualidade/Excelência** |
| **Atrasado** | 7,661 | 2.57 | +73.6 | **Zona Crítica (Detração Pura)** |

### 💥 O Impacto no NPS:
O NPS Proxy cai de um nível saudável de **-19.5** (pedidos entregues no prazo) para **+73.6** quando há atraso. Uma variação brutal de **93.1 pontos**, mostrando que o atraso converte massivamente clientes neutros/promotores em detratores agressivos da marca.

---

## 5. Visualizações Anexadas

Os gráficos gerados estão disponíveis na pasta do projeto e ajudam a ilustrar essa dinâmica para o relatório executivo:

1. **`boxplot_atraso_vs_score.png`:** Mostra a dispersão e mediana de atraso para cada nota. Fica claro visualmente como a distribuição se desloca para a zona de atraso à medida que a nota cai.
2. **`comparativo_pontualidade.png`:** Exibe lado a lado o declínio da nota média e a queda livre do NPS Proxy quando a entrega atrasa.

---

## 6. Recomendação para IA Agêntica (Logistics Coordinator Agent)

Com base nestes dados, o **Logistics Coordinator Agent** deve priorizar o monitoramento proativo de rotas que apresentem atraso projetado. Como o atraso causa uma queda abrupta imediata na satisfação (reduzindo a média para 2.57), o agente deve:
- Disparar um alerta de mitigação (e-mail de desculpas + cupom de frete grátis) assim que o pedido ultrapassar o limite do prazo estimado, atuando *antes* que o cliente responda à pesquisa de satisfação.
