# 📌 Status do Projeto e TODO List — Olist TechChallenge (Fase 1)

Este documento registra o progresso da sessão de planejamento de hoje (20 de Julho de 2026) e estabelece o roteiro exato para a retomada das atividades.

---

## 📂 1. Arquivos Gerados na Sessão de Hoje

Durante o planejamento, estruturamos os seguintes arquivos na pasta do subprojeto [TechChallenge](file:///c:/Users/paler/Documents/DataScience/POS%20TECH%20Agentes%20de%20IA/FASE%201/TechChallenge):

| Arquivo | Finalidade | Status |
| :--- | :--- | :--- |
| 📄 [analise_tratamento_dados.md](file:///c:/Users/paler/Documents/DataScience/POS%20TECH%20Agentes%20de%20IA/FASE%201/TechChallenge/analise_tratamento_dados.md) | Análise aprofundada com os prós e contras das abordagens de tratamento para produtos sem categoria e reviews duplicadas. | **Pronto para Decisão** |
| 📄 [plano_dataframe_unificado.md](file:///c:/Users/paler/Documents/DataScience/POS%20TECH%20Agentes%20de%20IA/FASE%201/TechChallenge/plano_dataframe_unificado.md) | Planejamento da arquitetura de Joins, cardinalidades, agregação e definição de features derivadas. | **Aprovado** |
| 🐍 [build_unified_dataframe.py](file:///c:/Users/paler/Documents/DataScience/POS%20TECH%20Agentes%20de%20IA/FASE%201/TechChallenge/build_unified_dataframe.py) | Script de pipeline pronto para ler os 9 CSVs, executar os joins descritos no plano e salvar a base em formato Parquet. | **Pronto para Execução** |

*Nota: O diagnóstico preliminar em Python foi executado e limpo com sucesso do workspace.*

---

## 📝 2. TODO List de Engenharia e Análise de Dados

Abaixo está o roteiro estruturado para as próximas etapas de desenvolvimento:

### Passo 1: Execução do Tratamento e Unificação (Conclusão do Passo 1 & 2)
- [ ] Executar o script [build_unified_dataframe.py](file:///c:/Users/paler/Documents/DataScience/POS%20TECH%20Agentes%20de%20IA/FASE%201/TechChallenge/build_unified_dataframe.py).
- [ ] Validar o output gerado em `discovery_output/olist_unified.parquet` (~30-40 MB).
- [ ] Validar o schema documentado em `discovery_output/olist_unified_schema.md`.

### Passo 3: Correlação Delivery Time × Review Score (Satisfação do Cliente)
- [ ] Criar script para calcular a correlação de Pearson/Spearman entre `delay_days` (ou `lead_time_days`) e o `review_score`.
- [ ] Gerar gráficos (boxplots de atrasos agregados por review score de 1 a 5).
- [ ] Exportar insights quantitativos detalhados (ex: "X dias de atraso reduzem a nota média em Y pontos").

### Passo 4: Segmentação RFM (Recency, Frequency, Monetary)
- [ ] Desenvolver script de cálculo de RFM no nível de `customer_unique_id`.
- [ ] Definir regras de corte ou aplicar algoritmo de clusterização (K-Means/DBSCAN).
- [ ] Cruzar os clusters de comportamento de compra com as métricas de NPS dos clientes.

### Passo 5: Elaboração do Relatório Final (Fase 1)
- [ ] Consolidar as análises dos passos anteriores em um documento executivo de 10 a 20 páginas (conforme diretrizes do Tech Challenge).
- [ ] Incluir os diagramas Mermaid da proposta conceitual dos agentes de IA (disponível no arquivo [proposal_agentic_ai_phase1.md](file:///c:/Users/paler/Documents/DataScience/POS%20TECH%20Agentes%20de%20IA/FASE%201/TechChallenge/proposal_agentic_ai_phase1.md)).
