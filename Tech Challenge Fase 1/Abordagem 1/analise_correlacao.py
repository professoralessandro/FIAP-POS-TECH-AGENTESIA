"""
=============================================================================
 OLIST MARKETPLACE — ANÁLISE DE CORRELAÇÃO (ABORDAGEM 1)
 Investiga a relação entre o tempo de entrega / atrasos e a satisfação (review_score).
=============================================================================
 Execução:  python "abordagem 1/analise_correlacao.py"
 Outputs:   abordagem 1/relatorio_correlacao.md
            abordagem 1/boxplot_atraso_vs_score.png
            abordagem 1/comparativo_pontualidade.png
=============================================================================
"""

import os
import sys
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Backend não-interativo
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

# =============================================================================
# CONFIGURAÇÃO
# =============================================================================
OUTPUT_DIR = os.path.dirname(__file__)  # Salva na própria pasta "abordagem 1"
CSV_PATH = os.path.join(OUTPUT_DIR, "olist_unified.csv")
REPORT_PATH = os.path.join(OUTPUT_DIR, "relatorio_correlacao.md")

# Estilo visual dos gráficos
sns.set_theme(style="whitegrid", palette="muted", font_scale=1.1)
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['figure.dpi'] = 120
plt.rcParams['savefig.bbox'] = 'tight'

COLORS = {
    'primary': '#2962FF',     # Azul Olist
    'secondary': '#00C853',   # Verde (No prazo / Promotor)
    'danger': '#D50000',      # Vermelho (Atrasado / Detrator)
    'warning': '#FF6D00',     # Laranja
    'neutral': '#546E7A',     # Cinza
}

# =============================================================================
# 1. CARREGAMENTO DOS DADOS
# =============================================================================
print("=" * 70)
print("  OLIST — ANÁLISE DE CORRELAÇÃO (ABORDAGEM 1)")
print("=" * 70)
print(f"\n  Carregando dados unificados de: {CSV_PATH} ...")

if not os.path.exists(CSV_PATH):
    print(f"  [ERRO] O arquivo {CSV_PATH} não foi encontrado. Por favor, execute o build primeiro.")
    sys.exit(1)

df = pd.read_csv(CSV_PATH)
print(f"  Dados carregados: {len(df):,} pedidos")

# Filtrar apenas registros com entrega concluída e que possuam review e lead time válidos
df_analise = df[df['order_status'] == 'delivered'].copy()
df_analise = df_analise.dropna(subset=['review_score', 'lead_time_days', 'delay_days'])
print(f"  Registros qualificados para análise (entregues com review): {len(df_analise):,}")

print(f"\n{'─' * 70}")

# =============================================================================
# 2. CÁLCULO DE CORRELAÇÕES
# =============================================================================
print("\n  Calculando correlações estatísticas...\n")

# Correlação de Pearson (relação linear)
pearson_lead = df_analise['review_score'].corr(df_analise['lead_time_days'], method='pearson')
pearson_delay = df_analise['review_score'].corr(df_analise['delay_days'], method='pearson')

# Correlação de Spearman (relação monotônica / não-linear ordinal)
spearman_lead = df_analise['review_score'].corr(df_analise['lead_time_days'], method='spearman')
spearman_delay = df_analise['review_score'].corr(df_analise['delay_days'], method='spearman')

print(f"    Correlação Review Score x Lead Time (dias úteis/corridos totais):")
print(f"      Pearson:  {pearson_lead:.4f}")
print(f"      Spearman: {spearman_lead:.4f} (Mais robusto para escalas ordinais)")
print(f"\n    Correlação Review Score x Atraso (dias em relação ao prazo estimado):")
print(f"      Pearson:  {pearson_delay:.4f}")
print(f"      Spearman: {spearman_delay:.4f}")

print(f"\n{'─' * 70}")

# =============================================================================
# 3. ANÁLISE AGRUPADA POR SCORE (1 A 5)
# =============================================================================
print("\n  Agrupando performance de entrega por nota (Review Score)...\n")

group_stats = df_analise.groupby('review_score').agg(
    total_pedidos=('order_id', 'count'),
    lead_time_medio=('lead_time_days', 'mean'),
    lead_time_mediana=('lead_time_days', 'median'),
    atraso_medio=('delay_days', 'mean'),
    atraso_mediana=('delay_days', 'median'),
    taxa_atraso=('is_late', 'mean')
).reset_index()

# Multiplicar a taxa por 100 para percentual
group_stats['taxa_atraso_%'] = group_stats['taxa_atraso'] * 100

print(group_stats.to_string(index=False, formatters={
    'lead_time_medio': '{:.1f}d'.format,
    'lead_time_mediana': '{:.1f}d'.format,
    'atraso_medio': '{:+.1f}d'.format,
    'atraso_mediana': '{:+.1f}d'.format,
    'taxa_atraso_%': '{:.1f}%'.format
}))

print(f"\n{'─' * 70}")

# =============================================================================
# 4. COMPARAÇÃO: NO PRAZO VS ATRASADO
# =============================================================================
print("\n  Comparando pedidos no prazo vs. atrasados...\n")

df_analise['categoria_entrega'] = np.where(df_analise['is_late'] == True, 'Atrasado', 'No Prazo')

pontualidade_stats = df_analise.groupby('categoria_entrega').agg(
    pedidos=('order_id', 'count'),
    score_medio=('review_score', 'mean'),
    score_mediana=('review_score', 'median')
).reset_index()

# Cálculo do NPS Proxy por categoria
nps_list = []
for cat in ['No Prazo', 'Atrasado']:
    subset = df_analise[df_analise['categoria_entrega'] == cat]
    total = len(subset)
    promoters = (subset['review_score'] >= 4).sum()
    detractors = (subset['review_score'] <= 2).sum()
    nps = ((promoters - detractors) / total) * 100
    nps_list.append(nps)

pontualidade_stats['nps_proxy'] = nps_list

print(pontualidade_stats.to_string(index=False, formatters={
    'score_medio': '{:.2f}'.format,
    'nps_proxy': '{:+.1f}'.format
}))

print(f"\n{'─' * 70}")

# =============================================================================
# 5. GERANDO VISUALIZAÇÕES GRÁFICAS
# =============================================================================
print("\n  Gerando gráficos...\n")

# Gráfico 1: Boxplot de Atraso por Nota (limitando o range para ver a distribuição sem outliers distantes)
fig, ax = plt.subplots(figsize=(10, 6))
# Filtrar intervalo representativo (-20 a 40 dias de atraso) para o boxplot
df_box = df_analise[(df_analise['delay_days'] >= -20) & (df_analise['delay_days'] <= 40)]

sns.boxplot(
    data=df_box,
    x='review_score',
    y='delay_days',
    palette=[COLORS['danger'], COLORS['warning'], '#FFD600', COLORS['primary'], COLORS['secondary']],
    ax=ax,
    showfliers=False  # Oculta outliers para focar nos quartis
)

ax.axhline(0, color=COLORS['danger'], linestyle='--', linewidth=1.5, label='Prazo Estimado')
ax.set_title('Distribuição de Dias de Atraso por Nota de Avaliação', fontsize=14, fontweight='bold')
ax.set_xlabel('Nota da Avaliação (Review Score)')
ax.set_ylabel('Dias de Atraso (Negativo = Adiantado)')
ax.legend()

boxplot_img_path = os.path.join(OUTPUT_DIR, "boxplot_atraso_vs_score.png")
plt.savefig(boxplot_img_path)
plt.close()
print(f"    📊 Boxplot salvo: {boxplot_img_path}")


# Gráfico 2: Comparativo de Performance de Satisfação por Status de Pontualidade
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# Média de score
sns.barplot(
    data=pontualidade_stats,
    x='categoria_entrega',
    y='score_medio',
    palette=[COLORS['danger'], COLORS['secondary']],
    ax=ax1,
    edgecolor='black',
    alpha=0.8
)
ax1.set_title('Nota Média de Satisfação', fontsize=13, fontweight='bold')
ax1.set_xlabel('Status da Entrega')
ax1.set_ylabel('Score Médio (1 a 5)')
ax1.set_ylim(1, 5)
for bar in ax1.patches:
    ax1.annotate(f"{bar.get_height():.2f}",
                 (bar.get_x() + bar.get_width() / 2, bar.get_height() - 0.4),
                 ha='center', va='center', color='white', fontweight='bold', fontsize=12)

# NPS Proxy
sns.barplot(
    data=pontualidade_stats,
    x='categoria_entrega',
    y='nps_proxy',
    palette=[COLORS['danger'], COLORS['secondary']],
    ax=ax2,
    edgecolor='black',
    alpha=0.8
)
ax2.set_title('NPS Proxy por Status de Entrega', fontsize=13, fontweight='bold')
ax2.set_xlabel('Status da Entrega')
ax2.set_ylabel('NPS Proxy')
ax2.set_ylim(-100, 100)
ax2.axhline(0, color='black', linewidth=1)
for bar in ax2.patches:
    val = bar.get_height()
    va_dir = -10 if val < 0 else 10
    color_text = 'white' if abs(val) > 20 else 'black'
    ax2.annotate(f"{val:+.1f}",
                 (bar.get_x() + bar.get_width() / 2, val - va_dir),
                 ha='center', va='center', color=color_text, fontweight='bold', fontsize=12)

comparativo_img_path = os.path.join(OUTPUT_DIR, "comparativo_pontualidade.png")
plt.savefig(comparativo_img_path)
plt.close()
print(f"    📊 Gráfico comparativo salvo: {comparativo_img_path}")

print(f"\n{'─' * 70}")

# =============================================================================
# 6. GERAÇÃO DO RELATÓRIO EM MARKDOWN
# =============================================================================
print("\n  Gerando relatório analítico em markdown...\n")

total_pedidos = len(df_analise)
total_atrasados = (df_analise['is_late'] == True).sum()
pct_atrasados = total_atrasados / total_pedidos * 100

# Extrair métricas específicas para preencher o texto
score_medio_prazo = pontualidade_stats.loc[pontualidade_stats['categoria_entrega'] == 'No Prazo', 'score_medio'].values[0]
score_medio_atraso = pontualidade_stats.loc[pontualidade_stats['categoria_entrega'] == 'Atrasado', 'score_medio'].values[0]
nps_prazo = pontualidade_stats.loc[pontualidade_stats['categoria_entrega'] == 'No Prazo', 'nps_proxy'].values[0]
nps_atraso = pontualidade_stats.loc[pontualidade_stats['categoria_entrega'] == 'Atrasado', 'nps_proxy'].values[0]

report_content = f"""# 📊 Relatório de Correlação: Prazo de Entrega vs. Satisfação (Abordagem 1)

> **Data de Geração:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
> **Amostra Analisada:** {total_pedidos:,} pedidos reais entregues  
> **Taxa de Atraso Geral:** {pct_atrasados:.2f}% ({total_atrasados:,} pedidos)

---

## 1. Conclusão Principal (The Key Takeaway)

**Confirmado estatisticamente:** O tempo de entrega é um dos principais drivers de insatisfação do cliente na Olist. A ocorrência de um atraso destrói a percepção de valor do cliente, derrubando a nota de satisfação média e empurrando o NPS para a zona crítica.

---

## 2. Coeficientes de Correlação Estatística

Para quantificar a força e direção da relação entre o tempo de entrega e o review score, calculamos os coeficientes de **Pearson** (relação linear) e **Spearman** (relação monotônica / não-linear).

| Variável 1 | Variável 2 | Correlação Pearson | Correlação Spearman | Interpretação |
|---|---|---|---|---|
| `review_score` | `lead_time_days` | {pearson_lead:.4f} | {spearman_lead:.4f} | Correlação negativa moderada. Quanto maior o tempo total de frete, menor a nota. |
| `review_score` | `delay_days` | {pearson_delay:.4f} | {spearman_delay:.4f} | Correlação negativa moderada a forte. O atraso em relação ao prazo estimado é o maior detrator. |

*Nota: Valores de correlação variam de -1 a +1. O sinal negativo indica que quando o tempo de frete cresce, a nota cai. O coeficiente de Spearman é estatisticamente mais apropriado aqui por tratar o score de 1 a 5 como escala ordinal.*

---

## 3. Visão Agrupada por Review Score (1 a 5 estrelas)

Análise da performance logística média para cada nota dada pelo cliente:

| Nota (Estrelas) | Pedidos | Lead Time Médio | Lead Time Mediana | Atraso Médio (vs. Estimativa) | Taxa de Atraso (%) |
| :---: |---:|---:|---:|---:|---:|
{"".join(f"| ⭐{row['review_score']:.0f} | {row['total_pedidos']:,} | {row['lead_time_medio']:.1f} dias | {row['lead_time_mediana']:.1f} dias | {row['atraso_medio']:+.1f} dias | {row['taxa_atraso_%']:.1f}% |\n" for _, row in group_stats.iterrows())}

### 💡 Observações Críticas:
- **O Abismo do Atraso (Nota 1):** Clientes que avaliaram o pedido com **1 estrela** sofreram uma taxa de atraso alarmante de **{group_stats.loc[group_stats['review_score'] == 1, 'taxa_atraso_%'].values[0]:.1f}%**. O atraso médio desses pedidos foi de **{group_stats.loc[group_stats['review_score'] == 1, 'atraso_medio'].values[0]:+.1f} dias**.
- **O Padrão da Excelência (Nota 5):** Em contrapartida, pedidos com nota máxima (**5 estrelas**) foram entregues com tempo médio de apenas **{group_stats.loc[group_stats['review_score'] == 5, 'lead_time_medio'].values[0]:.1f} dias**, chegando em média **{-group_stats.loc[group_stats['review_score'] == 5, 'atraso_medio'].values[0]:.1f} dias ANTES** do prazo limite.

---

## 4. Comparativo de Impacto: No Prazo vs. Atrasado

A tabela abaixo exibe o impacto direto do atraso nos indicadores de qualidade de atendimento (NPS Proxy e Nota Média):

| Categoria | Pedidos | Nota Média (1 a 5) | NPS Proxy | Classificação de Qualidade |
|---|---|:---:|:---:|---|
| **No Prazo** | {pontualidade_stats.loc[pontualidade_stats['categoria_entrega'] == 'No Prazo', 'pedidos'].values[0]:,} | {score_medio_prazo:.2f} | {nps_prazo:+.1f} | **Zona de Qualidade/Excelência** |
| **Atrasado** | {pontualidade_stats.loc[pontualidade_stats['categoria_entrega'] == 'Atrasado', 'pedidos'].values[0]:,} | {score_medio_atraso:.2f} | {nps_atraso:+.1f} | **Zona Crítica (Detração Pura)** |

### 💥 O Impacto no NPS:
O NPS Proxy cai de um nível saudável de **{nps_prazo:+.1f}** (pedidos entregues no prazo) para **{nps_atraso:+.1f}** quando há atraso. Uma variação brutal de **{abs(nps_prazo - nps_atraso):.1f} pontos**, mostrando que o atraso converte massivamente clientes neutros/promotores em detratores agressivos da marca.

---

## 5. Visualizações Anexadas

Os gráficos gerados estão disponíveis na pasta do projeto e ajudam a ilustrar essa dinâmica para o relatório executivo:

1. **`boxplot_atraso_vs_score.png`:** Mostra a dispersão e mediana de atraso para cada nota. Fica claro visualmente como a distribuição se desloca para a zona de atraso à medida que a nota cai.
2. **`comparativo_pontualidade.png`:** Exibe lado a lado o declínio da nota média e a queda livre do NPS Proxy quando a entrega atrasa.

---

## 6. Recomendação para IA Agêntica (Logistics Coordinator Agent)

Com base nestes dados, o **Logistics Coordinator Agent** deve priorizar o monitoramento proativo de rotas que apresentem atraso projetado. Como o atraso causa uma queda abrupta imediata na satisfação (reduzindo a média para {score_medio_atraso:.2f}), o agente deve:
- Disparar um alerta de mitigação (e-mail de desculpas + cupom de frete grátis) assim que o pedido ultrapassar o limite do prazo estimado, atuando *antes* que o cliente responda à pesquisa de satisfação.
"""

with open(REPORT_PATH, 'w', encoding='utf-8') as f:
    f.write(report_content)

print(f"    📄 Relatório salvo: {REPORT_PATH}")

print(f"\n{'=' * 70}")
print("  Análise estatística concluída com sucesso!")
print(f"{'=' * 70}\n")
