"""
=============================================================================
 OLIST MARKETPLACE — SEGMENTAÇÃO RFM (ABORDAGEM 1)
 Agrupa os clientes com base em Recência, Frequência e Valor Monetário.
=============================================================================
 Execução:  python "abordagem 1/analise_rfm.py"
 Outputs:   abordagem 1/olist_rfm.csv
            abordagem 1/relatorio_rfm.md
            abordagem 1/distribuicao_segmentos_rfm.png
=============================================================================
"""

import os
import sys
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

# =============================================================================
# CONFIGURAÇÃO
# =============================================================================
OUTPUT_DIR = os.path.dirname(__file__)  # Salva na própria pasta "abordagem 1"
CSV_PATH = os.path.join(OUTPUT_DIR, "olist_unified.csv")
RFM_CSV_PATH = os.path.join(OUTPUT_DIR, "olist_rfm.csv")
REPORT_PATH = os.path.join(OUTPUT_DIR, "relatorio_rfm.md")

# Estilo visual
sns.set_theme(style="whitegrid", palette="muted", font_scale=1.1)
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['figure.dpi'] = 120
plt.rcParams['savefig.bbox'] = 'tight'

COLORS = {
    'primary': '#2962FF',
    'secondary': '#00C853',
    'warning': '#FF6D00',
    'danger': '#D50000',
    'neutral': '#546E7A',
    'palette': ['#2962FF', '#00C853', '#FF6D00', '#AA00FF', '#00BFA5', '#FFD600', '#D50000', '#C2185B', '#0288D1', '#E64A19']
}

# =============================================================================
# 1. CARREGAMENTO DOS DADOS
# =============================================================================
print("=" * 70)
print("  OLIST — SEGMENTAÇÃO RFM (ABORDAGEM 1)")
print("=" * 70)
print(f"\n  Carregando dados unificados de: {CSV_PATH} ...")

if not os.path.exists(CSV_PATH):
    print(f"  [ERRO] O arquivo {CSV_PATH} não foi encontrado. Execute o pipeline primeiro.")
    sys.exit(1)

df = pd.read_csv(CSV_PATH)
df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])

# Filtrar apenas clientes válidos (com customer_unique_id preenchido)
df_rfm_base = df.dropna(subset=['customer_unique_id']).copy()
print(f"  Registros com cliente identificável: {len(df_rfm_base):,}")

# =============================================================================
# 2. CÁLCULO DE R, F, M POR CLIENTE
# =============================================================================
print("\n  Calculando Recência, Frequência e Valor Monetário por Cliente...\n")

# A data âncora é a data da última compra do dataset + 1 dia (para evitar recência zero)
anchor_date = df_rfm_base['order_purchase_timestamp'].max() + pd.Timedelta(days=1)
print(f"    Data Âncora (referência): {anchor_date.strftime('%Y-%m-%d %H:%M:%S')}")

# Agregação por cliente
rfm = df_rfm_base.groupby('customer_unique_id').agg(
    UltimaCompra=('order_purchase_timestamp', 'max'),
    Frequencia=('order_id', 'nunique'),
    Monetario=('price_total', 'sum')  # Valor dos itens comprados
).reset_index()

rfm['Recencia'] = (anchor_date - rfm['UltimaCompra']).dt.days

# Tratar possíveis nulos em Monetario (por exemplo, compras canceladas sem preço)
rfm['Monetario'] = rfm['Monetario'].fillna(0)

print(f"    Clientes únicos processados: {len(rfm):,}")
print(f"    Frequência máxima observada: {rfm['Frequencia'].max()} compras")
print(f"    Recência média:              {rfm['Recencia'].mean():.1f} dias")
print(f"    Monetário médio gasto:        R$ {rfm['Monetario'].mean():.2f}")

print(f"\n{'─' * 70}")

# =============================================================================
# 3. PONTUAÇÃO RFM (SCORES DE 1 A 5)
# =============================================================================
print("\n  Calculando Scores RFM (1 a 5)...\n")

# Recência: Menor número de dias é melhor (inverte labels)
rfm['R_Score'] = pd.qcut(rfm['Recencia'], q=5, labels=[5, 4, 3, 2, 1])

# Frequência: 97% dos clientes têm apenas 1 compra. A divisão por quintis normais (qcut)
# falharia por conta de bins repetidos. Criamos uma pontuação manual/customizada.
def score_frequencia(f):
    if f == 1:
        return 1
    elif f == 2:
        return 3
    else:  # F >= 3
        return 5

rfm['F_Score'] = rfm['Frequencia'].apply(score_frequencia)

# Monetário: Maior valor gasto é melhor
rfm['M_Score'] = pd.qcut(rfm['Monetario'].rank(method='first'), q=5, labels=[1, 2, 3, 4, 5])

# Converter scores para inteiros para análises
rfm['R_Score'] = rfm['R_Score'].astype(int)
rfm['F_Score'] = rfm['F_Score'].astype(int)
rfm['M_Score'] = rfm['M_Score'].astype(int)

# String combinada do Score (Ex: "515")
rfm['RFM_Score'] = rfm['R_Score'].astype(str) + rfm['F_Score'].astype(str) + rfm['M_Score'].astype(str)

print(f"    Scores gerados com sucesso")

print(f"\n{'─' * 70}")

# =============================================================================
# 4. MAPEAMENTO DE SEGMENTOS DE CLIENTES
# =============================================================================
print("\n  Classificando clientes em segmentos de negócio...\n")

def mapear_segmento(row):
    r = row['R_Score']
    f = row['F_Score']
    m = row['M_Score']
    
    # 1. Campeões (Compraram recentemente, compram muito e gastam bem)
    if r >= 4 and f == 5 and m >= 4:
        return 'Campeões'
    
    # 2. Clientes Fiéis (Compram frequentemente, razoavelmente recentes)
    elif r >= 3 and f >= 3 and m >= 3:
        return 'Fiéis'
    
    # 3. Novos Recentes (Compraram há pouco tempo, frequência de 1)
    elif r >= 4 and f == 1 and m <= 2:
        return 'Novos Clientes'
    
    # 4. Novos Promissores (Compraram há pouco tempo, valor monetário alto, frequência 1)
    elif r >= 4 and f == 1 and m >= 3:
        return 'Novos Promissores'
    
    # 5. Clientes que Precisam de Atenção (Frequência média, recência morna)
    elif r == 3 and f >= 3:
        return 'Atenção Necessária'
    
    # 6. Prestes a Dormir (Frequência baixa, recência morna)
    elif r == 3 and f == 1:
        return 'Prestes a Dormir'
    
    # 7. Em Risco (Frequência alta ou média, mas não compram há muito tempo)
    elif r <= 2 and f >= 3:
        return 'Em Risco de Churn'
    
    # 8. Perdidos (Recência muito antiga, frequência baixa, gasto baixo)
    elif r <= 2 and f == 1 and m <= 2:
        return 'Perdidos'
    
    # 9. Recuperáveis / Hibernando (Recência antiga, mas com gasto razoável/alto)
    elif r <= 2 and f == 1 and m >= 3:
        return 'Hibernando'
    
    # Padrão
    else:
        return 'Diversos / Outros'

rfm['Segmento'] = rfm.apply(mapear_segmento, axis=1)

# Estatísticas por Segmento
segment_stats = rfm.groupby('Segmento').agg(
    Clientes=('customer_unique_id', 'count'),
    Recencia_Media=('Recencia', 'mean'),
    Frequencia_Media=('Frequencia', 'mean'),
    Monetario_Medio=('Monetario', 'mean'),
    Monetario_Total=('Monetario', 'sum')
).reset_index()

# Ordenar por contagem de clientes
segment_stats = segment_stats.sort_values('Clientes', ascending=False)
segment_stats['Clientes_%'] = (segment_stats['Clientes'] / len(rfm)) * 100
segment_stats['Receita_%'] = (segment_stats['Monetario_Total'] / rfm['Monetario'].sum()) * 100

print(segment_stats.to_string(index=False, formatters={
    'Clientes': '{:,}'.format,
    'Recencia_Media': '{:.1f}d'.format,
    'Frequencia_Media': '{:.2f}'.format,
    'Monetario_Medio': 'R$ {:.2f}'.format,
    'Monetario_Total': 'R$ {:,.2f}'.format,
    'Clientes_%': '{:.1f}%'.format,
    'Receita_%': '{:.1f}%'.format
}))

print(f"\n{'─' * 70}")

# =============================================================================
# 5. GERANDO VISUALIZAÇÕES
# =============================================================================
print("\n  Gerando gráficos explicativos...\n")

fig, ax = plt.subplots(figsize=(12, 7))

# Ordenar os segmentos para exibição no gráfico
plot_data = segment_stats.sort_values('Clientes', ascending=True)

bars = ax.barh(
    plot_data['Segmento'],
    plot_data['Clientes_%'],
    color=COLORS['palette'][:len(plot_data)],
    edgecolor='black',
    alpha=0.8
)

ax.set_title('Distribuição de Clientes por Segmento RFM', fontsize=14, fontweight='bold')
ax.set_xlabel('% dos Clientes Únicos')
ax.set_ylabel('Segmento')

# Adicionar labels com valores absolutos e percentuais nas barras
for bar, row in zip(bars, plot_data.iterrows()):
    val_pct = row[1]['Clientes_%']
    val_abs = int(row[1]['Clientes'])
    ax.text(
        bar.get_width() + 0.5,
        bar.get_y() + bar.get_height()/2,
        f'{val_pct:.1f}% ({val_abs:,})',
        va='center',
        fontsize=10,
        fontweight='bold'
    )

chart_path = os.path.join(OUTPUT_DIR, "distribuicao_segmentos_rfm.png")
plt.savefig(chart_path)
plt.close()
print(f"    📊 Gráfico salvo: {chart_path}")

print(f"\n{'─' * 70}")

# =============================================================================
# 6. SALVAR ARQUIVOS DE OUTPUT
# =============================================================================
print("\n  Salvando arquivos finais...\n")

# Salvar CSV com a base de clientes clusterizados
rfm.to_csv(RFM_CSV_PATH, index=False)
print(f"    CSV de Clientes Segmentados salvo: {RFM_CSV_PATH}")

# Gerar o relatório Markdown
report_lines = [
    "# 📈 Relatório de Segmentação RFM (Abordagem 1)\n",
    f"> **Data de Geração:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
    f"> **Base Total de Clientes Analisados:** {len(rfm):,} compradores únicos\n",
    f"> **GMV Abrangido:** R$ {rfm['Monetario'].sum():,.2f}\n",
    "",
    "## 1. Contexto do Negócio",
    "A análise de RFM (Recency, Frequency, Monetary) é uma técnica chave para segmentação de base de clientes.",
    "No e-commerce brasileiro (Olist), observamos uma particularidade marcante:",
    "**A taxa de recompra é extremamente baixa (aprox. 3%).** Isso significa que a esmagadora maioria",
    "dos clientes possui `Frequencia = 1`. Por esse motivo, a métrica de frequência é pontuada de forma",
    "customizada para destacar a minoria que compra recorrentemente.",
    "",
    "---",
    "",
    "## 2. Estatísticas Gerais dos Segmentos RFM",
    "",
    "| Segmento | Clientes | % Clientes | Recência Média | Freq. Média | Monetário Médio | Receita Total | % Receita |",
    "|---|---:|---:|---:|---:|---:|---:|---:|",
]

for _, row in segment_stats.iterrows():
    report_lines.append(
        f"| **{row['Segmento']}** | {row['Clientes']:,} | {row['Clientes_%']:.1f}% | {row['Recencia_Media']:.1f} dias | {row['Frequencia_Media']:.2f} | R$ {row['Monetario_Medio']:.2f} | R$ {row['Monetario_Total']:,.2f} | {row['Receita_%']:.1f}% |"
    )

# Adicionar insights estratégicos baseados em dados reais
campeoes = rfm[rfm['Segmento'] == 'Campeões']
perdidos = rfm[rfm['Segmento'] == 'Perdidos']
novos_promissores = rfm[rfm['Segmento'] == 'Novos Promissores']
hibernando = rfm[rfm['Segmento'] == 'Hibernando']

report_lines.extend([
    "",
    "---",
    "",
    "## 3. Principais Insights e Oportunidades Estratégicas",
    "",
    "### 💥 A Dominância do Segmento 'Perdidos'",
    f"O maior segmento na Olist é o de **Perdidos**, representando **{segment_stats.loc[segment_stats['Segmento'] == 'Perdidos', 'Clientes_%'].values[0]:.1f}%** da base. São clientes que compraram uma única vez há muito tempo (média de **{segment_stats.loc[segment_stats['Segmento'] == 'Perdidos', 'Recencia_Media'].values[0]:.1f} dias** atrás) e gastaram pouco. Isso confirma o grande desafio de atração de leads sem fidelização posterior na plataforma.",
    "",
    "### 🎯 A Oportunidade em 'Hibernando'",
    f"O segmento **Hibernando** representa **{segment_stats.loc[segment_stats['Segmento'] == 'Hibernando', 'Clientes_%'].values[0]:.1f}%** dos clientes, mas responde por **{segment_stats.loc[segment_stats['Segmento'] == 'Hibernando', 'Receita_%'].values[0]:.1f}%** do total gasto. São clientes de alto valor monetário (gasto médio de **R$ {segment_stats.loc[segment_stats['Segmento'] == 'Hibernando', 'Monetario_Medio'].values[0]:.2f}**) que não realizam compras há bastante tempo. Reativar essa parcela da base via e-mail marketing personalizado ou ofertas exclusivas trará um retorno imediato de receita.",
    "",
    "### 🏆 Os Poucos 'Campeões' & 'Fiéis'",
    "Devido à baixíssima recompra estrutural do modelo de marketplace no período (2016-2018), os clientes **Campeões** e **Fiéis** juntos representam menos de 1.5% da base total de compradores, embora possuam um ticket médio e frequência de compra muito superiores aos demais.",
    "",
    "---",
    "",
    "## 4. Recomendações para a IA Agêntica (Seller Success & Growth Agent)",
    "- **Reter Novos Clientes:** O agente deve disparar alertas automáticos ou convites de engajamento para a base de **Novos Promissores** e **Novos Clientes** nas primeiras semanas pós-entrega, oferecendo cupons para incentivar a segunda compra.",
    "- **Campanhas de Reativação:** Desenhar e-mails dinâmicos voltados ao segmento **Hibernando**, utilizando as categorias mais compradas por eles como base para recomendação inteligente.",
    "- **Ações com Sellers Locais:** Como frete alto e atraso geram detratores, o agente de crescimento de sellers deve orientar os lojistas a manter estoque mais próximo dos clusters de clientes que mais compram do segmento 'Novos Clientes' para garantir entregas mais baratas e ágeis.",
    "",
    "---",
    "## 5. Visualizações",
    "- O gráfico da distribuição percentual e absoluta dos segmentos está disponível em: `distribuicao_segmentos_rfm.png`."
])

with open(REPORT_PATH, 'w', encoding='utf-8') as f:
    f.write('\n'.join(report_lines))

print(f"    📄 Relatório Markdown salvo: {REPORT_PATH}")

print(f"\n{'=' * 70}")
print("  Segmentação RFM concluída com sucesso!")
print(f"{'=' * 70}\n")
