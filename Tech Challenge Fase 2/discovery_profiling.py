"""
=============================================================================
 OLIST MARKETPLACE — DISCOVERY DATA PROFILING
 Estudo de Caso: Brazilian E-Commerce Public Dataset by Olist
 Fonte: https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce/data
=============================================================================
 Este script executa o checklist de qualidade dos dados e gera
 um relatório completo com estatísticas, distribuições e visualizações.
=============================================================================
"""

import os
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Backend não-interativo para salvar PNGs
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
from datetime import datetime

# =============================================================================
# CONFIGURAÇÃO
# =============================================================================
DATA_DIR = os.path.join(os.path.dirname(__file__), "OLIST Dataset")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "discovery_output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Estilo visual
sns.set_theme(style="whitegrid", palette="muted", font_scale=1.1)
plt.rcParams['figure.figsize'] = (14, 6)
plt.rcParams['figure.dpi'] = 120
plt.rcParams['savefig.bbox'] = 'tight'

COLORS = {
    'primary': '#2962FF',
    'secondary': '#00C853',
    'warning': '#FF6D00',
    'danger': '#D50000',
    'neutral': '#546E7A',
    'palette': ['#2962FF', '#00C853', '#FF6D00', '#AA00FF', '#00BFA5', '#FFD600', '#D50000']
}

# =============================================================================
# 1. CARREGAMENTO DOS DADOS
# =============================================================================
print("=" * 70)
print("  OLIST DISCOVERY — DATA PROFILING")
print("=" * 70)
print(f"\n📂 Carregando dados de: {DATA_DIR}\n")

datasets = {}
files = {
    'orders':       'olist_orders_dataset.csv',
    'items':        'olist_order_items_dataset.csv',
    'payments':     'olist_order_payments_dataset.csv',
    'reviews':      'olist_order_reviews_dataset.csv',
    'customers':    'olist_customers_dataset.csv',
    'products':     'olist_products_dataset.csv',
    'sellers':      'olist_sellers_dataset.csv',
    'geolocation':  'olist_geolocation_dataset.csv',
    'categories':   'product_category_name_translation.csv',
}

for name, filename in files.items():
    filepath = os.path.join(DATA_DIR, filename)
    df = pd.read_csv(filepath)
    datasets[name] = df
    print(f"  ✅ {name:15s} → {len(df):>10,} linhas × {len(df.columns)} colunas  ({filename})")

print(f"\n{'─' * 70}")

# =============================================================================
# 2. CONVERSÃO DE TIPOS (DATAS)
# =============================================================================
print("\n🔧 Convertendo colunas de data/hora...\n")

date_columns = {
    'orders': [
        'order_purchase_timestamp', 'order_approved_at',
        'order_delivered_carrier_date', 'order_delivered_customer_date',
        'order_estimated_delivery_date'
    ],
    'items': ['shipping_limit_date'],
    'reviews': ['review_creation_date', 'review_answer_timestamp'],
}

for table, cols in date_columns.items():
    for col in cols:
        datasets[table][col] = pd.to_datetime(datasets[table][col], errors='coerce')
        print(f"  📅 {table}.{col}")

print(f"\n{'─' * 70}")

# =============================================================================
# 3. RELATÓRIO DE NULOS
# =============================================================================
print("\n📊 ANÁLISE DE VALORES NULOS\n")

null_report = []
for name, df in datasets.items():
    total = len(df)
    for col in df.columns:
        n_null = df[col].isnull().sum()
        pct = (n_null / total) * 100
        if n_null > 0:
            null_report.append({
                'Dataset': name,
                'Coluna': col,
                'Nulos': n_null,
                '% Nulos': round(pct, 2),
                'Total Linhas': total
            })

if null_report:
    df_nulls = pd.DataFrame(null_report).sort_values('% Nulos', ascending=False)
    print(df_nulls.to_string(index=False))
    df_nulls.to_csv(os.path.join(OUTPUT_DIR, "01_null_report.csv"), index=False)
    print(f"\n  💾 Salvo em: discovery_output/01_null_report.csv")

    # Gráfico de nulos
    fig, ax = plt.subplots(figsize=(14, max(6, len(df_nulls) * 0.35)))
    df_nulls_plot = df_nulls.head(20).copy()
    df_nulls_plot['label'] = df_nulls_plot['Dataset'] + '.' + df_nulls_plot['Coluna']
    bars = ax.barh(df_nulls_plot['label'], df_nulls_plot['% Nulos'],
                   color=[COLORS['danger'] if p > 50 else COLORS['warning'] if p > 10 else COLORS['primary']
                          for p in df_nulls_plot['% Nulos']])
    ax.set_xlabel('% de Valores Nulos')
    ax.set_title('Top 20 — Colunas com Valores Nulos', fontsize=14, fontweight='bold')
    ax.invert_yaxis()
    for bar, pct in zip(bars, df_nulls_plot['% Nulos']):
        ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2,
                f'{pct:.1f}%', va='center', fontsize=9)
    plt.savefig(os.path.join(OUTPUT_DIR, "01_null_analysis.png"))
    plt.close()
    print(f"  📊 Gráfico salvo: discovery_output/01_null_analysis.png")
else:
    print("  ✅ Nenhum valor nulo encontrado em nenhum dataset!")

print(f"\n{'─' * 70}")

# =============================================================================
# 4. VERIFICAÇÃO DE CHAVES PRIMÁRIAS (DUPLICATAS)
# =============================================================================
print("\n🔑 VERIFICAÇÃO DE CHAVES PRIMÁRIAS\n")

pk_checks = {
    'orders': 'order_id',
    'customers': 'customer_id',
    'products': 'product_id',
    'sellers': 'seller_id',
    'reviews': 'review_id',
}

for name, pk in pk_checks.items():
    df = datasets[name]
    total = len(df)
    unique = df[pk].nunique()
    dupes = total - unique
    status = "✅ OK" if dupes == 0 else f"⚠️ {dupes:,} duplicatas!"
    print(f"  {name:15s} → PK: {pk:30s} | Total: {total:>10,} | Únicos: {unique:>10,} | {status}")

print(f"\n{'─' * 70}")

# =============================================================================
# 5. DISTRIBUIÇÃO DE ORDER_STATUS
# =============================================================================
print("\n📋 DISTRIBUIÇÃO DE STATUS DOS PEDIDOS\n")

orders = datasets['orders']
status_counts = orders['order_status'].value_counts()
status_pct = (status_counts / len(orders) * 100).round(2)

for status, count in status_counts.items():
    pct = status_pct[status]
    bar = "█" * int(pct / 2)
    print(f"  {status:20s} → {count:>8,}  ({pct:>6.2f}%)  {bar}")

# Gráfico
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

# Pie chart
colors_pie = COLORS['palette'][:len(status_counts)]
ax1.pie(status_counts.values, labels=status_counts.index, autopct='%1.1f%%',
        colors=colors_pie, startangle=90, pctdistance=0.85)
ax1.set_title('Distribuição de Status dos Pedidos', fontsize=13, fontweight='bold')

# Bar chart sem "delivered" para ver os outros
status_no_delivered = status_counts.drop('delivered', errors='ignore')
ax2.bar(status_no_delivered.index, status_no_delivered.values, color=COLORS['palette'][1:])
ax2.set_title('Status (excluindo "delivered") — Detalhe', fontsize=13, fontweight='bold')
ax2.set_ylabel('Quantidade')
plt.xticks(rotation=45, ha='right')
plt.savefig(os.path.join(OUTPUT_DIR, "02_order_status_distribution.png"))
plt.close()
print(f"\n  📊 Gráfico salvo: discovery_output/02_order_status_distribution.png")

print(f"\n{'─' * 70}")

# =============================================================================
# 6. CONSISTÊNCIA DE DATAS
# =============================================================================
print("\n📅 VERIFICAÇÃO DE CONSISTÊNCIA DE DATAS\n")

delivered = orders[orders['order_status'] == 'delivered'].copy()

# Aprovação antes da compra?
issue1 = (delivered['order_approved_at'] < delivered['order_purchase_timestamp']).sum()
# Entrega ao carrier antes da aprovação?
issue2 = (delivered['order_delivered_carrier_date'] < delivered['order_approved_at']).sum()
# Entrega ao cliente antes do carrier?
issue3 = (delivered['order_delivered_customer_date'] < delivered['order_delivered_carrier_date']).sum()

print(f"  Pedidos entregues analisados: {len(delivered):,}")
print(f"  ⚠️ Aprovação < Compra:       {issue1:>6,} ocorrências")
print(f"  ⚠️ Carrier < Aprovação:      {issue2:>6,} ocorrências")
print(f"  ⚠️ Cliente < Carrier:        {issue3:>6,} ocorrências")

# Lead times
delivered['lead_time_days'] = (
    delivered['order_delivered_customer_date'] - delivered['order_purchase_timestamp']
).dt.total_seconds() / 86400

delivered['delay_days'] = (
    delivered['order_delivered_customer_date'] - delivered['order_estimated_delivery_date']
).dt.total_seconds() / 86400

delayed = (delivered['delay_days'] > 0).sum()
on_time = (delivered['delay_days'] <= 0).sum()
pct_delayed = delayed / len(delivered) * 100

print(f"\n  ⏱️ Lead Time (compra → entrega ao cliente):")
print(f"     Mínimo:  {delivered['lead_time_days'].min():.1f} dias")
print(f"     Médio:   {delivered['lead_time_days'].mean():.1f} dias")
print(f"     Mediana: {delivered['lead_time_days'].median():.1f} dias")
print(f"     Máximo:  {delivered['lead_time_days'].max():.1f} dias")
print(f"\n  🚚 Entregas atrasadas: {delayed:,} ({pct_delayed:.1f}%)")
print(f"  ✅ Entregas no prazo:  {on_time:,} ({100 - pct_delayed:.1f}%)")

# Gráfico lead time e atrasos
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

# Lead time distribution
lead_clean = delivered['lead_time_days'].dropna()
lead_clean = lead_clean[(lead_clean >= 0) & (lead_clean <= 60)]
ax1.hist(lead_clean, bins=60, color=COLORS['primary'], alpha=0.8, edgecolor='white')
ax1.axvline(lead_clean.mean(), color=COLORS['danger'], linestyle='--', linewidth=2, label=f'Média: {lead_clean.mean():.1f}d')
ax1.axvline(lead_clean.median(), color=COLORS['secondary'], linestyle='--', linewidth=2, label=f'Mediana: {lead_clean.median():.1f}d')
ax1.set_xlabel('Dias')
ax1.set_ylabel('Frequência')
ax1.set_title('Distribuição do Lead Time (Compra → Entrega)', fontsize=13, fontweight='bold')
ax1.legend()

# Delay distribution
delay_clean = delivered['delay_days'].dropna()
delay_clean = delay_clean[(delay_clean >= -30) & (delay_clean <= 60)]
colors_hist = [COLORS['secondary'] if x <= 0 else COLORS['danger'] for x in np.linspace(delay_clean.min(), delay_clean.max(), 50)]
ax2.hist(delay_clean, bins=50, color=COLORS['neutral'], alpha=0.8, edgecolor='white')
ax2.axvline(0, color=COLORS['danger'], linestyle='-', linewidth=2, label='Prazo estimado')
ax2.set_xlabel('Dias (negativo = antes do prazo, positivo = atraso)')
ax2.set_ylabel('Frequência')
ax2.set_title(f'Atraso na Entrega (atrasados: {pct_delayed:.1f}%)', fontsize=13, fontweight='bold')
ax2.legend()

plt.savefig(os.path.join(OUTPUT_DIR, "03_delivery_timing.png"))
plt.close()
print(f"\n  📊 Gráfico salvo: discovery_output/03_delivery_timing.png")

print(f"\n{'─' * 70}")

# =============================================================================
# 7. ANÁLISE DE REVIEWS
# =============================================================================
print("\n⭐ ANÁLISE DE REVIEW SCORES\n")

reviews = datasets['reviews']
score_counts = reviews['review_score'].value_counts().sort_index()
score_pct = (score_counts / len(reviews) * 100).round(2)

for score in range(1, 6):
    count = score_counts.get(score, 0)
    pct = score_pct.get(score, 0)
    stars = "⭐" * score
    bar = "█" * int(pct / 2)
    print(f"  {stars:12s} ({score}) → {count:>8,}  ({pct:>6.2f}%)  {bar}")

# Reviews com comentário
has_title = reviews['review_comment_title'].notna().sum()
has_message = reviews['review_comment_message'].notna().sum()
print(f"\n  💬 Reviews com título:    {has_title:>8,} ({has_title/len(reviews)*100:.1f}%)")
print(f"  💬 Reviews com mensagem:  {has_message:>8,} ({has_message/len(reviews)*100:.1f}%)")

# NPS Proxy
promoters = reviews[reviews['review_score'] >= 4].shape[0]
detractors = reviews[reviews['review_score'] <= 2].shape[0]
nps = (promoters - detractors) / len(reviews) * 100
print(f"\n  📈 NPS Proxy: {nps:.1f} (Promotores: {promoters:,} | Detratores: {detractors:,})")

# Gráfico de scores
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

score_colors = [COLORS['danger'], COLORS['warning'], '#FFD600', COLORS['secondary'], COLORS['primary']]
ax1.bar(score_counts.index, score_counts.values, color=score_colors, edgecolor='white', linewidth=1.5)
ax1.set_xlabel('Nota')
ax1.set_ylabel('Quantidade')
ax1.set_title('Distribuição dos Review Scores', fontsize=13, fontweight='bold')
ax1.set_xticks([1, 2, 3, 4, 5])

# NPS gauge (horizontal stacked bar)
nps_data = {
    'Detratores (1-2)': detractors / len(reviews) * 100,
    'Neutros (3)': reviews[reviews['review_score'] == 3].shape[0] / len(reviews) * 100,
    'Promotores (4-5)': promoters / len(reviews) * 100,
}
nps_colors = [COLORS['danger'], '#FFD600', COLORS['secondary']]
left = 0
for (label, val), color in zip(nps_data.items(), nps_colors):
    ax2.barh(0, val, left=left, color=color, label=f'{label}: {val:.1f}%', height=0.5)
    left += val
ax2.set_xlim(0, 100)
ax2.set_yticks([])
ax2.set_xlabel('% dos Reviews')
ax2.set_title(f'NPS Proxy: {nps:.1f}', fontsize=13, fontweight='bold')
ax2.legend(loc='lower center', bbox_to_anchor=(0.5, -0.3), ncol=3)

plt.savefig(os.path.join(OUTPUT_DIR, "04_review_scores.png"))
plt.close()
print(f"\n  📊 Gráfico salvo: discovery_output/04_review_scores.png")

print(f"\n{'─' * 70}")

# =============================================================================
# 8. ANÁLISE DE PAGAMENTOS
# =============================================================================
print("\n💳 ANÁLISE DE PAGAMENTOS\n")

payments = datasets['payments']
payment_type_counts = payments['payment_type'].value_counts()
payment_type_pct = (payment_type_counts / len(payments) * 100).round(2)

for ptype, count in payment_type_counts.items():
    pct = payment_type_pct[ptype]
    bar = "█" * int(pct / 2)
    print(f"  {ptype:20s} → {count:>8,}  ({pct:>6.2f}%)  {bar}")

# Parcelas
installments = payments[payments['payment_type'] == 'credit_card']['payment_installments']
print(f"\n  📊 Parcelas (cartão de crédito):")
print(f"     Média:   {installments.mean():.1f} parcelas")
print(f"     Mediana: {installments.median():.0f} parcelas")
print(f"     Máximo:  {installments.max():.0f} parcelas")

# Gráfico
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

ax1.pie(payment_type_counts.values, labels=payment_type_counts.index,
        autopct='%1.1f%%', colors=COLORS['palette'][:len(payment_type_counts)],
        startangle=90, pctdistance=0.85)
ax1.set_title('Distribuição por Tipo de Pagamento', fontsize=13, fontweight='bold')

inst_counts = installments.value_counts().sort_index().head(12)
ax2.bar(inst_counts.index, inst_counts.values, color=COLORS['primary'], edgecolor='white')
ax2.set_xlabel('Número de Parcelas')
ax2.set_ylabel('Quantidade')
ax2.set_title('Distribuição de Parcelas (Cartão de Crédito)', fontsize=13, fontweight='bold')
ax2.set_xticks(inst_counts.index)

plt.savefig(os.path.join(OUTPUT_DIR, "05_payment_analysis.png"))
plt.close()
print(f"\n  📊 Gráfico salvo: discovery_output/05_payment_analysis.png")

print(f"\n{'─' * 70}")

# =============================================================================
# 9. ANÁLISE DE CATEGORIAS DE PRODUTO
# =============================================================================
print("\n🏷️ ANÁLISE DE CATEGORIAS DE PRODUTO\n")

products = datasets['products']
categories = datasets['categories']

# Nulos em categorias
cat_null = products['product_category_name'].isnull().sum()
cat_total = len(products)
print(f"  Produtos sem categoria: {cat_null:,} ({cat_null/cat_total*100:.2f}%)")

# Cobertura da tradução
unique_cats = products['product_category_name'].dropna().unique()
translated_cats = set(categories['product_category_name'].values)
not_translated = set(unique_cats) - translated_cats
print(f"  Categorias únicas:      {len(unique_cats)}")
print(f"  Categorias traduzidas:  {len(translated_cats)}")
print(f"  Sem tradução:           {len(not_translated)}")
if not_translated:
    print(f"    → {not_translated}")

# Top 15 categorias
items = datasets['items']
product_items = items.merge(products[['product_id', 'product_category_name']], on='product_id', how='left')
product_items = product_items.merge(categories, on='product_category_name', how='left')

cat_revenue = product_items.groupby('product_category_name_english').agg(
    total_revenue=('price', 'sum'),
    total_items=('order_item_id', 'count'),
    avg_price=('price', 'mean')
).sort_values('total_revenue', ascending=False).head(15)

print(f"\n  🏆 Top 15 Categorias por Receita:")
for i, (cat, row) in enumerate(cat_revenue.iterrows(), 1):
    print(f"  {i:>3}. {cat:35s} R$ {row['total_revenue']:>12,.2f}  ({row['total_items']:>6,} itens)")

# Gráfico
fig, ax = plt.subplots(figsize=(14, 8))
cat_plot = cat_revenue.sort_values('total_revenue', ascending=True)
bars = ax.barh(cat_plot.index, cat_plot['total_revenue'], color=COLORS['primary'], edgecolor='white')
ax.set_xlabel('Receita Total (R$)')
ax.set_title('Top 15 Categorias por Receita', fontsize=14, fontweight='bold')
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: f'R$ {x:,.0f}'))

plt.savefig(os.path.join(OUTPUT_DIR, "06_top_categories.png"))
plt.close()
print(f"\n  📊 Gráfico salvo: discovery_output/06_top_categories.png")

print(f"\n{'─' * 70}")

# =============================================================================
# 10. ANÁLISE GEOGRÁFICA
# =============================================================================
print("\n🌍 ANÁLISE GEOGRÁFICA\n")

customers = datasets['customers']
sellers = datasets['sellers']

# Clientes por estado
cust_state = customers['customer_state'].value_counts().head(10)
print("  👤 Top 10 Estados — Clientes:")
for state, count in cust_state.items():
    pct = count / len(customers) * 100
    bar = "█" * int(pct / 2)
    print(f"  {state:5s} → {count:>8,}  ({pct:>5.1f}%)  {bar}")

# Vendedores por estado
sell_state = sellers['seller_state'].value_counts().head(10)
print("\n  🏪 Top 10 Estados — Vendedores:")
for state, count in sell_state.items():
    pct = count / len(sellers) * 100
    bar = "█" * int(pct)
    print(f"  {state:5s} → {count:>6,}  ({pct:>5.1f}%)  {bar}")

# Gráfico
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))

ax1.barh(cust_state.index[::-1], cust_state.values[::-1], color=COLORS['primary'], edgecolor='white')
ax1.set_xlabel('Quantidade de Clientes')
ax1.set_title('Top 10 Estados — Clientes', fontsize=13, fontweight='bold')

ax2.barh(sell_state.index[::-1], sell_state.values[::-1], color=COLORS['secondary'], edgecolor='white')
ax2.set_xlabel('Quantidade de Vendedores')
ax2.set_title('Top 10 Estados — Vendedores', fontsize=13, fontweight='bold')

plt.savefig(os.path.join(OUTPUT_DIR, "07_geographic_distribution.png"))
plt.close()
print(f"\n  📊 Gráfico salvo: discovery_output/07_geographic_distribution.png")

print(f"\n{'─' * 70}")

# =============================================================================
# 11. EVOLUÇÃO TEMPORAL DAS VENDAS
# =============================================================================
print("\n📈 EVOLUÇÃO TEMPORAL DAS VENDAS\n")

orders_items = orders.merge(items[['order_id', 'price', 'freight_value']], on='order_id', how='left')
orders_items['year_month'] = orders_items['order_purchase_timestamp'].dt.to_period('M')

monthly = orders_items.groupby('year_month').agg(
    n_orders=('order_id', 'nunique'),
    total_revenue=('price', 'sum'),
    total_freight=('freight_value', 'sum')
).reset_index()

monthly['year_month_str'] = monthly['year_month'].astype(str)
monthly['gmv'] = monthly['total_revenue'] + monthly['total_freight']
monthly['aov'] = monthly['gmv'] / monthly['n_orders']

print(f"  Período: {monthly['year_month_str'].iloc[0]} a {monthly['year_month_str'].iloc[-1]}")
print(f"  Meses com dados: {len(monthly)}")
print(f"  GMV Total: R$ {monthly['gmv'].sum():,.2f}")
print(f"  Total de Pedidos: {monthly['n_orders'].sum():,}")
print(f"  AOV Geral: R$ {monthly['gmv'].sum() / monthly['n_orders'].sum():.2f}")

# Gráfico
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 10))

x = range(len(monthly))
labels = monthly['year_month_str'].values

ax1.fill_between(x, monthly['total_revenue'], alpha=0.3, color=COLORS['primary'])
ax1.plot(x, monthly['total_revenue'], color=COLORS['primary'], linewidth=2, marker='o', markersize=4, label='Receita (Produtos)')
ax1.fill_between(x, monthly['total_freight'], alpha=0.3, color=COLORS['secondary'])
ax1.plot(x, monthly['total_freight'], color=COLORS['secondary'], linewidth=2, marker='s', markersize=4, label='Frete')
ax1.set_title('Evolução Mensal — Receita e Frete', fontsize=14, fontweight='bold')
ax1.set_ylabel('R$')
ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: f'R$ {x:,.0f}'))
ax1.legend()
ax1.set_xticks(x[::2])
ax1.set_xticklabels(labels[::2], rotation=45, ha='right')

ax2.bar(x, monthly['n_orders'], color=COLORS['primary'], alpha=0.7, edgecolor='white')
ax2.plot(x, monthly['aov'], color=COLORS['danger'], linewidth=2, marker='o', markersize=4)
ax2_twin = ax2.twinx()
ax2_twin.plot(x, monthly['aov'], color=COLORS['danger'], linewidth=2, marker='o', markersize=4, label='AOV (R$)')
ax2_twin.set_ylabel('AOV (R$)', color=COLORS['danger'])
ax2.set_title('Evolução Mensal — Volume de Pedidos e Ticket Médio', fontsize=14, fontweight='bold')
ax2.set_ylabel('Nº de Pedidos')
ax2.set_xticks(x[::2])
ax2.set_xticklabels(labels[::2], rotation=45, ha='right')
# Remove duplicate line from ax2
ax2.lines[0].remove()

plt.savefig(os.path.join(OUTPUT_DIR, "08_sales_evolution.png"))
plt.close()
print(f"\n  📊 Gráfico salvo: discovery_output/08_sales_evolution.png")

print(f"\n{'─' * 70}")

# =============================================================================
# 12. TAXA DE RECOMPRA
# =============================================================================
print("\n🔄 ANÁLISE DE RECOMPRA\n")

cust_orders = customers.merge(orders[['order_id', 'customer_id']], on='customer_id')
unique_buyers = customers['customer_unique_id'].nunique()
total_orders_per_buyer = cust_orders.groupby('customer_unique_id')['order_id'].nunique()

repeat_buyers = (total_orders_per_buyer > 1).sum()
repeat_rate = repeat_buyers / unique_buyers * 100

print(f"  Compradores únicos:     {unique_buyers:>10,}")
print(f"  Compradores recorrentes: {repeat_buyers:>10,} ({repeat_rate:.2f}%)")
print(f"  Compradores únicos (1x): {unique_buyers - repeat_buyers:>10,} ({100 - repeat_rate:.2f}%)")

orders_dist = total_orders_per_buyer.value_counts().sort_index().head(10)
print(f"\n  📊 Distribuição de pedidos por comprador:")
for n_orders, count in orders_dist.items():
    print(f"     {n_orders} pedido(s): {count:>8,} compradores")

print(f"\n{'─' * 70}")

# =============================================================================
# 13. OUTLIERS EM PREÇO E FRETE
# =============================================================================
print("\n📦 ANÁLISE DE OUTLIERS (Preço e Frete)\n")

for col_name, col in [('Preço', 'price'), ('Frete', 'freight_value')]:
    data = items[col]
    q1, q3 = data.quantile(0.25), data.quantile(0.75)
    iqr = q3 - q1
    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr
    n_outliers = ((data < lower) | (data > upper)).sum()
    pct_outliers = n_outliers / len(data) * 100

    print(f"  {col_name}:")
    print(f"     Min:      R$ {data.min():>10,.2f}")
    print(f"     Q1:       R$ {q1:>10,.2f}")
    print(f"     Mediana:  R$ {data.median():>10,.2f}")
    print(f"     Média:    R$ {data.mean():>10,.2f}")
    print(f"     Q3:       R$ {q3:>10,.2f}")
    print(f"     Max:      R$ {data.max():>10,.2f}")
    print(f"     IQR:      R$ {iqr:>10,.2f}")
    print(f"     Outliers: {n_outliers:>6,} ({pct_outliers:.1f}%)")
    print()

# Gráfico boxplot
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

bp1 = ax1.boxplot(items['price'].dropna(), vert=True, patch_artist=True,
                  boxprops=dict(facecolor=COLORS['primary'], alpha=0.6),
                  medianprops=dict(color=COLORS['danger'], linewidth=2))
ax1.set_title('Boxplot — Preço dos Itens', fontsize=13, fontweight='bold')
ax1.set_ylabel('R$')

bp2 = ax2.boxplot(items['freight_value'].dropna(), vert=True, patch_artist=True,
                  boxprops=dict(facecolor=COLORS['secondary'], alpha=0.6),
                  medianprops=dict(color=COLORS['danger'], linewidth=2))
ax2.set_title('Boxplot — Valor do Frete', fontsize=13, fontweight='bold')
ax2.set_ylabel('R$')

plt.savefig(os.path.join(OUTPUT_DIR, "09_price_freight_outliers.png"))
plt.close()
print(f"  📊 Gráfico salvo: discovery_output/09_price_freight_outliers.png")

# =============================================================================
# 14. CONSISTÊNCIA PAGAMENTOS vs ITENS
# =============================================================================
print(f"\n{'─' * 70}")
print("\n💰 CONSISTÊNCIA: PAGAMENTOS vs. ITENS DO PEDIDO\n")

item_totals = items.groupby('order_id').agg(
    item_total=('price', 'sum'),
    freight_total=('freight_value', 'sum')
).reset_index()
item_totals['item_gmv'] = item_totals['item_total'] + item_totals['freight_total']

payment_totals = payments.groupby('order_id')['payment_value'].sum().reset_index()
payment_totals.columns = ['order_id', 'payment_total']

comparison = item_totals.merge(payment_totals, on='order_id', how='inner')
comparison['diff'] = abs(comparison['item_gmv'] - comparison['payment_total'])
comparison['match'] = comparison['diff'] < 1.0  # tolerância de R$1

matched = comparison['match'].sum()
total_comp = len(comparison)
print(f"  Pedidos comparados:   {total_comp:>10,}")
print(f"  ✅ Valores consistentes (diff < R$1): {matched:>8,} ({matched/total_comp*100:.1f}%)")
print(f"  ⚠️ Com divergência:                   {total_comp - matched:>8,} ({(total_comp-matched)/total_comp*100:.1f}%)")

if total_comp - matched > 0:
    divergent = comparison[~comparison['match']].sort_values('diff', ascending=False)
    print(f"\n  Top 5 maiores divergências:")
    for _, row in divergent.head(5).iterrows():
        print(f"    Pedido: {row['order_id'][:12]}... | Itens: R$ {row['item_gmv']:.2f} | Pgto: R$ {row['payment_total']:.2f} | Diff: R$ {row['diff']:.2f}")

# =============================================================================
# 15. GEOLOCALIZAÇÃO - DUPLICIDADE
# =============================================================================
print(f"\n{'─' * 70}")
print("\n🌐 ANÁLISE DE DUPLICIDADE — GEOLOCALIZAÇÃO\n")

geo = datasets['geolocation']
cep_counts = geo['geolocation_zip_code_prefix'].value_counts()
unique_ceps = cep_counts.nunique()

print(f"  Total de registros:    {len(geo):>12,}")
print(f"  CEPs únicos:           {unique_ceps:>12,}")
print(f"  Média de registros/CEP: {cep_counts.mean():>11.1f}")
print(f"  Máximo de registros/CEP: {cep_counts.max():>10,}")
print(f"  CEPs com 1 registro:   {(cep_counts == 1).sum():>12,}")
print(f"  CEPs com >100 registros: {(cep_counts > 100).sum():>10,}")

# =============================================================================
# SUMÁRIO FINAL
# =============================================================================
print(f"\n{'=' * 70}")
print("  📋 SUMÁRIO DO DISCOVERY")
print(f"{'=' * 70}\n")

summary = {
    'Total de Pedidos': f"{len(orders):,}",
    'Período': f"{monthly['year_month_str'].iloc[0]} a {monthly['year_month_str'].iloc[-1]}",
    'GMV Total': f"R$ {monthly['gmv'].sum():,.2f}",
    'AOV': f"R$ {monthly['gmv'].sum() / monthly['n_orders'].sum():.2f}",
    'Categorias de Produto': f"{len(unique_cats)}",
    'Vendedores': f"{len(sellers):,}",
    'Clientes Únicos': f"{unique_buyers:,}",
    'Taxa de Recompra': f"{repeat_rate:.2f}%",
    'NPS Proxy': f"{nps:.1f}",
    'Taxa Entrega no Prazo (OTIF)': f"{100 - pct_delayed:.1f}%",
    'Lead Time Médio': f"{delivered['lead_time_days'].mean():.1f} dias",
    'Forma Pagamento Dominante': f"Cartão de Crédito ({payment_type_pct.iloc[0]:.1f}%)",
}

for key, value in summary.items():
    print(f"  {key:35s} → {value}")

print(f"\n{'=' * 70}")
print(f"  ✅ Relatório completo salvo em: {OUTPUT_DIR}")
print(f"  📊 {len([f for f in os.listdir(OUTPUT_DIR) if f.endswith('.png')])} gráficos gerados")
print(f"  📄 {len([f for f in os.listdir(OUTPUT_DIR) if f.endswith('.csv')])} relatórios CSV gerados")
print(f"{'=' * 70}\n")

# Salvar sumário em CSV
pd.DataFrame(list(summary.items()), columns=['Métrica', 'Valor']).to_csv(
    os.path.join(OUTPUT_DIR, "00_summary.csv"), index=False
)

print("🏁 Discovery concluído com sucesso!")
