# 📊 Estrutura de Slides — Apresentação Executiva Olist (Google Slides)

> **Projeto:** Tech Challenge — Fase 1 (IA Agêntica no Olist)  
> **Arquivos Sincronizados:** [relatorio_executivo.md](file:///c:/Users/paler/Documents/DataScience/POS%20TECH%20Agentes%20de%20IA/FASE%201/TechChallenge/Abordagem%201/relatorio_executivo.md) | [roteiro_video_executivo.md](file:///c:/Users/paler/Documents/DataScience/POS%20TECH%20Agentes%20de%20IA/FASE%201/TechChallenge/Abordagem%201/roteiro_video_executivo.md)  
> **Formato:** Guia slide a slide para criação rápida no Google Slides / PowerPoint (ou utilização da versão HTML interativa gerada [apresentacao_executiva.html](file:///c:/Users/paler/Documents/DataScience/POS%20TECH%20Agentes%20de%20IA/FASE%201/TechChallenge/Abordagem%201/apresentacao_executiva.html)).

---

## 🖥️ SLIDE 1: Capa Executiva

* **Título Principal:** Transformação em IA Agêntica
* **Subtítulo:** Estratégia de Inteligência Artificial para Qualidade Logística, CX e Escala no Olist
* **Linha de Apoio:** Tech Challenge — Fase 1 | Pós-Graduação em Agentes de IA
* **Elementos Visuais Sugeridos:** Logo da Olist em destaque, visual moderno em tons de azul escuro/verde neon, ícone de rede de agentes conectados.

```text
[NOTAS DO APRESENTADOR - 0:00 a 0:45]
"Olá, diretoria da Olist. Apresentamos hoje a estratégia de IA Agêntica desenhada para transformar os principais gargalos operacionais da plataforma em alavancas de crescimento e satisfação."
```

---

## 🖥️ SLIDE 2: Diagnóstico do Negócio — Dores & Dados

* **Título:** Diagnóstico dos Dados: As Dores Reais da Operação
* **Grid de 3 Métricas Destacadas (Cartões de KPI):**
  1. **8,1% de Atraso Logístico:** Principal destruidor da experiência do cliente.
  2. **-93 Pontos de NPS:** Entregas no prazo possuem NPS de **+73,6**; entregas atrasadas caem para **-19,5** (Nota média despenca de 4.29 para 2.57).
  3. **33,7% da Receita Ameaçada:** O grupo de clientes 'Hibernantes' representa 1/3 da receita histórica, mas está sem comprar há mais de 14 meses (recompra geral de apenas 3,1%).
* **Elemento Visual:** Gráfico comparativo de Nota Média (No Prazo vs Atrasado) e gráfico de pizza da segmentação RFM.

```text
[NOTAS DO APRESENTADOR - 0:45 a 2:00]
"Nossos dados revelam que o atraso logístico derruba o NPS de +73 para -19. Além disso, 33,7% do faturamento está concentrado em clientes hibernantes com alta propensão de churn."
```

---

## 🖥️ SLIDE 3: O Mapa de Agentes de IA (A Solução)

* **Título:** Solução Proposta: Ecossistema de 3 Agentes Inteligentes
* **3 Colunas de Agentes (Cartões Executivos):**

  | 🤖 Review Intelligence Agent | 🚚 Logistics Coordinator Agent | 📈 Seller Success & Growth Agent |
  | :--- | :--- | :--- |
  | **Foco:** NPS & Atendimento ao Cliente | **Foco:** SLA Logístico & Operações | **Foco:** Engajamento & Retenção de Sellers |
  | • Classificação de causa raiz em tempo real | • Previsão de risco de atraso em trânsito | • Mentoria automatizada em 3 passos |
  | • Rascunho de resposta empática ao cliente | • Notificação preventiva ao cliente | • Capacitação de lojistas fora de SP (hoje 60% em SP) |
  | • Alerta imediato de SKUs defeituosos | • Alertas de gargalos por transportadora | • Reativação do segmento 'Hibernante' |

```text
[NOTAS DO APRESENTADOR - 2:00 a 3:45]
"Propomos 3 agentes especializados: um focado em CX para tratar o review na hora, outro focado em salvar prazos logísticos preventivamente e um terceiro focado em capacitar lojistas."
```

---

## 🖥️ SLIDE 4: Arquitetura Conceitual Inicial

* **Título:** Arquitetura Integrada: Como os Agentes se Conectam
* **Estrutura em 3 Camadas:**
  1. **Ingestão:** Base Unificada (`olist_unified.csv`) + Base de Reviews + Segmentação RFM.
  2. **Camada Agêntica:** Orquestrador de Eventos + Comunicação direta entre Agente Logístico e Agente de CX.
  3. **Saída Operacional:** CRM de Clientes, Painel Interno de Operações e Portal do Lojista.
* **Elemento Visual:** Diagrama de fluxo de dados (utilizar o diagrama Mermaid do relatório final convertido em imagem visual).

```text
[NOTAS DO APRESENTADOR - 3:45 a 4:30]
"A arquitetura conecta a base de dados unificada a um orquestrador central. Quando o agente de logística detecta um atraso, ele já prepara o agente de atendimento para acolher o cliente."
```

---

## 🖥️ SLIDE 5: Impacto de Negócio & Próximos Passos (Fase 2)

* **Título:** Retorno Esperado & Roadmap de Implementação
* **Retorno de Negócio (ROI):**
  * 🛡️ **Proteção da Marca:** Redução da detração ativa e respostas instantâneas a reviews Nota 1.
  * 💰 **Alavancagem de Receita:** Reativação da base hibernante (33,7% da receita).
  * ⚡ **Escala Operacional:** Suporte automatizado sem aumento de custo fixo com atendimento.
* **Próximos Passos (Fase 2):**
  1. Conexão dos Prompts Estruturados com LLMs (LangChain/LangGraph).
  2. Pipeline de dados em tempo real.
  3. Validação qualitativa das respostas dos agentes.

```text
[NOTAS DO APRESENTADOR - 4:30 a 5:00]
"Na Fase 2, conectaremos essa inteligência a modelos de linguagem para rodar o piloto real. Agradeço a atenção de todos!"
```
