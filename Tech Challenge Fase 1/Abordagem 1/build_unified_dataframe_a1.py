"""
=============================================================================
 OLIST MARKETPLACE — BUILD UNIFIED DATAFRAME (ABORDAGEM 1)
 Granularidade: 1 linha = 1 pedido (aprox. 99.441 linhas).
=============================================================================
 Execução:  python "abordagem 1/build_unified_dataframe_a1.py"
 Outputs:   abordagem 1/olist_unified.csv
            abordagem 1/olist_unified_schema.md
=============================================================================
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

# =============================================================================
# CONFIGURAÇÃO
# =============================================================================
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, "OLIST Dataset")
OUTPUT_DIR = os.path.dirname(__file__)  # Salva na própria pasta "abordagem 1"

CSV_PATH = os.path.join(OUTPUT_DIR, "olist_unified.csv")
SCHEMA_PATH = os.path.join(OUTPUT_DIR, "olist_unified_schema.md")

# =============================================================================
# 1. CARREGAMENTO DOS DADOS
# =============================================================================
print("=" * 70)
print("  OLIST — BUILD UNIFIED DATAFRAME (ABORDAGEM 1)")
print("=" * 70)
print(f"\n  Início: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"  Fonte:  {DATA_DIR}\n")

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

ds = {}
for name, filename in files.items():
    filepath = os.path.join(DATA_DIR, filename)
    df = pd.read_csv(filepath)
    ds[name] = df
    print(f"  OK  {name:15s}  {len(df):>10,} linhas x {len(df.columns)} colunas")

print(f"\n{'─' * 70}")

# =============================================================================
# 2. CONVERSÃO DE TIPOS (DATAS)
# =============================================================================
print("\n  Convertendo colunas de data/hora...\n")

date_cols = {
    'orders': [
        'order_purchase_timestamp', 'order_approved_at',
        'order_delivered_carrier_date', 'order_delivered_customer_date',
        'order_estimated_delivery_date'
    ],
    'reviews': ['review_creation_date', 'review_answer_timestamp'],
}

for table, cols in date_cols.items():
    for col in cols:
        ds[table][col] = pd.to_datetime(ds[table][col], errors='coerce')
        print(f"    {table}.{col}")

print(f"\n{'─' * 70}")

# =============================================================================
# 3. TRATAMENTO: PRODUTOS SEM CATEGORIA
# =============================================================================
print("\n  Tratando produtos sem categoria...\n")

n_null_cat = ds['products']['product_category_name'].isnull().sum()
ds['products']['product_category_name'] = (
    ds['products']['product_category_name'].fillna('sem_categoria')
)
print(f"    {n_null_cat} produtos rotulados como 'sem_categoria'")

# Adicionar tradução para sem_categoria
new_row = pd.DataFrame({
    'product_category_name': ['sem_categoria'],
    'product_category_name_english': ['uncategorized']
})
ds['categories'] = pd.concat([ds['categories'], new_row], ignore_index=True)
print(f"    Tradução 'sem_categoria' -> 'uncategorized' adicionada")

print(f"\n{'─' * 70}")

# =============================================================================
# 4. AGREGAÇÃO: GEOLOCALIZAÇÃO
# =============================================================================
print("\n  Agregando coordenadas de geolocalização por CEP (mediana)...\n")

geo_agg = ds['geolocation'].groupby('geolocation_zip_code_prefix').agg(
    geolocation_lat=('geolocation_lat', 'median'),
    geolocation_lng=('geolocation_lng', 'median')
).reset_index()

print(f"    {len(ds['geolocation']):,} linhas -> {len(geo_agg):,} CEPs únicos agregados")

print(f"\n{'─' * 70}")

# =============================================================================
# 5. DEDUPLICAÇÃO DE REVIEWS (Antes do Join)
# =============================================================================
print("\n  Deduplicando reviews por order_id (mantendo a primeira)...\n")

n_before_reviews = len(ds['reviews'])
reviews_dedup = ds['reviews'].drop_duplicates(subset='order_id', keep='first')
n_after_reviews = len(reviews_dedup)

print(f"    Reviews originais: {n_before_reviews:,} -> Deduplicadas: {n_after_reviews:,}")

print(f"\n{'─' * 70}")

# =============================================================================
# 6. AGREGAÇÃO DE ITEMS (112k linhas -> 99k linhas por pedido)
# =============================================================================
print("\n  Agregando itens por pedido (order_id) para nível de pedido...\n")

# Para podermos trazer os metadados de produto e seller no nível de pedido,
# precisamos identificar o produto/seller principal do pedido (aqui definimos como o primeiro inserido)
items_sorted = ds['items'].sort_values(['order_id', 'order_item_id'])

items_agg = items_sorted.groupby('order_id').agg(
    price_total=('price', 'sum'),
    freight_total=('freight_value', 'sum'),
    items_count=('order_item_id', 'count'),
    unique_products_count=('product_id', 'nunique'),
    unique_sellers_count=('seller_id', 'nunique'),
    main_product_id=('product_id', 'first'),
    main_seller_id=('seller_id', 'first')
).reset_index()

print(f"    Itens de pedidos: {len(ds['items']):,} -> Pedidos com itens: {len(items_agg):,}")

print(f"\n{'─' * 70}")

# =============================================================================
# 7. PRE-AGREGAÇÃO: PAYMENTS (103k linhas -> 99k por pedido)
# =============================================================================
print("\n  Pre-agregando payments por order_id...\n")

payments_agg = ds['payments'].groupby('order_id').agg(
    payment_value_total=('payment_value', 'sum'),
    payment_installments_max=('payment_installments', 'max'),
    payment_type_main=('payment_type', lambda x: x.value_counts().index[0] if len(x) > 0 else np.nan),
    n_payment_methods=('payment_sequential', 'nunique'),
).reset_index()

print(f"    Payments originais: {len(ds['payments']):,} -> Agregados por pedido: {len(payments_agg):,}")
print(f"\n{'─' * 70}")

# =============================================================================
# 8. JOINS SEQUENCIAIS (Granularidade Pedido: 99.441 linhas)
# =============================================================================
print("\n  Executando joins sequenciais no nível de Pedido...\n")

# Tabela âncora: orders (todos os pedidos)
df = ds['orders'].copy()
print(f"    [ÂNCORA] orders: {len(df):,} linhas")

# Join 1: + items agregados (order_id)
df = df.merge(items_agg, on='order_id', how='left')
print(f"    [JOIN 1] + items (agg)     -> {len(df):,} linhas")

# Join 2: + customers (customer_id)
df = df.merge(ds['customers'], on='customer_id', how='left')
print(f"    [JOIN 2] + customers       -> {len(df):,} linhas")

# Join 3: + products (main_product_id)
products_cols = [
    'product_id', 'product_category_name', 'product_weight_g',
    'product_length_cm', 'product_height_cm', 'product_width_cm'
]
df = df.merge(
    ds['products'][products_cols].rename(columns={'product_id': 'main_product_id'}),
    on='main_product_id',
    how='left'
)
print(f"    [JOIN 3] + products (main)  -> {len(df):,} linhas")

# Join 4: + category_translation (product_category_name)
df = df.merge(ds['categories'], on='product_category_name', how='left')
print(f"    [JOIN 4] + categories      -> {len(df):,} linhas")

# Join 5: + sellers (main_seller_id)
sellers_renamed = ds['sellers'].rename(columns={
    'seller_id': 'main_seller_id',
    'seller_zip_code_prefix': 'seller_zip_code_prefix',
    'seller_city': 'seller_city',
    'seller_state': 'seller_state',
})
df = df.merge(sellers_renamed, on='main_seller_id', how='left')
print(f"    [JOIN 5] + sellers (main)   -> {len(df):,} linhas")

# Join 6: + reviews_dedup (order_id)
reviews_cols = [
    'order_id', 'review_id', 'review_score',
    'review_comment_title', 'review_comment_message',
    'review_creation_date', 'review_answer_timestamp'
]
df = df.merge(reviews_dedup[reviews_cols], on='order_id', how='left')
print(f"    [JOIN 6] + reviews (dedup)  -> {len(df):,} linhas")

# Join 7: + payments_agg (order_id)
df = df.merge(payments_agg, on='order_id', how='left')
print(f"    [JOIN 7] + payments (agg)  -> {len(df):,} linhas")

# Join 8: + customer geoloc (customer_zip_code_prefix)
df = df.merge(
    geo_agg.rename(columns={
        'geolocation_zip_code_prefix': 'customer_zip_code_prefix',
        'geolocation_lat': 'customer_lat',
        'geolocation_lng': 'customer_lng'
    }),
    on='customer_zip_code_prefix',
    how='left'
)
print(f"    [JOIN 8] + customer geo    -> {len(df):,} linhas")

# Join 9: + seller geoloc (seller_zip_code_prefix)
df = df.merge(
    geo_agg.rename(columns={
        'geolocation_zip_code_prefix': 'seller_zip_code_prefix',
        'geolocation_lat': 'seller_lat',
        'geolocation_lng': 'seller_lng'
    }),
    on='seller_zip_code_prefix',
    how='left'
)
print(f"    [JOIN 9] + seller geo      -> {len(df):,} linhas")

print(f"\n{'─' * 70}")

# =============================================================================
# 9. FEATURES DERIVADAS
# =============================================================================
print("\n  Criando features derivadas...\n")

# Tempos logísticos
df['lead_time_days'] = (
    df['order_delivered_customer_date'] - df['order_purchase_timestamp']
).dt.total_seconds() / 86400

df['delay_days'] = (
    df['order_delivered_customer_date'] - df['order_estimated_delivery_date']
).dt.total_seconds() / 86400

df['is_late'] = (df['delay_days'] > 0).astype('boolean')

df['approval_time_hours'] = (
    df['order_approved_at'] - df['order_purchase_timestamp']
).dt.total_seconds() / 3600

# Temporal
df['purchase_year_month'] = df['order_purchase_timestamp'].dt.to_period('M').astype(str)
df['purchase_dow'] = df['order_purchase_timestamp'].dt.dayofweek
df['purchase_hour'] = df['order_purchase_timestamp'].dt.hour

# Financeiro
df['freight_ratio'] = np.where(
    df['price_total'] > 0,
    df['freight_total'] / df['price_total'],
    np.nan
)

# NLP flag
df['has_review_text'] = df['review_comment_message'].notna()

# Logística geográfica
df['is_cross_state'] = (df['seller_state'] != df['customer_state'])

features_created = [
    'lead_time_days', 'delay_days', 'is_late', 'approval_time_hours',
    'purchase_year_month', 'purchase_dow', 'purchase_hour',
    'freight_ratio', 'has_review_text', 'is_cross_state'
]
for f in features_created:
    print(f"    + {f}")

print(f"\n    Total de features derivadas: {len(features_created)}")
print(f"\n{'─' * 70}")

# =============================================================================
# 10. VALIDAÇÕES
# =============================================================================
print("\n  Executando validações...\n")

checks = []

# Contagem de linhas (deve ser exatamente igual a orders original)
n_rows = len(df)
orders_original = len(ds['orders'])
status_rows = 'OK' if n_rows == orders_original else f'ALERTA: {n_rows} vs {orders_original}'
checks.append(('Contagem de linhas (pedidos)', f'{n_rows:,}', status_rows))

# Contagem de colunas
checks.append(('Contagem de colunas', f'{len(df.columns)}', 'INFO'))

# Nulos críticos
for col in ['order_id', 'order_status', 'customer_id']:
    n_null = df[col].isnull().sum()
    status = 'OK' if n_null == 0 else f'ALERTA: {n_null} nulos'
    checks.append((f'Nulos em {col}', str(n_null), status))

# Nulos em reviews
n_null_review = df['review_score'].isnull().sum()
checks.append((
    'Pedidos sem review',
    f'{n_null_review:,}',
    'INFO'
))

# Geolocalização preenchida (%)
cust_geo_ok = df['customer_lat'].notnull().sum()
checks.append((
    'Clientes c/ Lat/Lng (%)',
    f'{cust_geo_ok/n_rows*100:.1f}%',
    'OK' if cust_geo_ok/n_rows > 0.95 else 'ALERTA'
))

# Receitas
revenue_original = ds['items']['price'].sum()
revenue_unified = df['price_total'].sum()
checks.append((
    'Receita original (price)',
    f'R$ {revenue_original:,.2f}',
    'INFO'
))
checks.append((
    'Receita no unificado',
    f'R$ {revenue_unified:,.2f}',
    'OK' if abs(revenue_original - revenue_unified) < 1.0 else 'ALERTA (Itens órfãos/sem pedido?)'
))

for label, value, status in checks:
    icon = '  OK ' if 'OK' in status else ' INFO' if status == 'INFO' else ' !!! '
    print(f"    [{icon}] {label:45s}  {value:>15s}  {status}")

print(f"\n{'─' * 70}")

# =============================================================================
# 11. SALVAR OUTPUT
# =============================================================================
print(f"\n  Salvando outputs...\n")

# CSV
df.to_csv(CSV_PATH, index=False, encoding='utf-8')
csv_size = os.path.getsize(CSV_PATH) / (1024 * 1024)
print(f"    CSV: {CSV_PATH}")
print(f"    Tamanho: {csv_size:.1f} MB")

# Documentação de Schema
schema_lines = [
    "# Schema do DataFrame Unificado Olist — Abordagem 1\n",
    f"> **Gerado em:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
    f"> **Granularidade:** Pedido (Order-level)\n",
    f"> **Linhas (pedidos):** {len(df):,} | **Colunas:** {len(df.columns)}\n",
    "",
    "## ⚙️ Decisões Aplicadas nesta Abordagem:",
    "- **Geolocalização:** Integrada com mediana por CEP para clientes e vendedores.",
    "- **Produtos sem Categoria:** Substituídos por `'sem_categoria'`.",
    "- **Reviews:** Deduplicados por `order_id` mantendo o primeiro registro.",
    "- **Granularidade:** Agregada no nível de pedido (`order_id`). Itens e valores financeiros somados.",
    "- **Formato de Saída:** CSV.",
    "",
    "## 📋 Dicionário de Colunas:",
    "",
    "| # | Coluna | Tipo | Nulos | % Nulos | Origem | Descrição |",
    "|---|---|---|---:|---:|---|---|",
]

for i, col in enumerate(df.columns, 1):
    dtype = str(df[col].dtype)
    n_null = df[col].isnull().sum()
    pct_null = n_null / len(df) * 100

    # Determinar origem
    if col in ['price_total', 'freight_total', 'items_count', 'unique_products_count', 'unique_sellers_count', 'main_product_id', 'main_seller_id']:
        origin = 'order_items (agg)'
    elif col in ds['orders'].columns:
        origin = 'orders'
    elif col in ds['customers'].columns:
        origin = 'customers'
    elif col in ['product_category_name', 'product_weight_g', 'product_length_cm', 'product_height_cm', 'product_width_cm']:
        origin = 'products'
    elif col in ['seller_zip_code_prefix', 'seller_city', 'seller_state']:
        origin = 'sellers'
    elif col in ds['reviews'].columns:
        origin = 'reviews'
    elif col in payments_agg.columns:
        origin = 'payments (agg)'
    elif col in ds['categories'].columns:
        origin = 'categories'
    elif col in ['customer_lat', 'customer_lng', 'seller_lat', 'seller_lng']:
        origin = 'geolocation (agg)'
    elif col in features_created:
        origin = '**DERIVADA**'
    else:
        origin = '—'

    schema_lines.append(
        f"| {i} | `{col}` | {dtype} | {n_null:,} | {pct_null:.1f}% | {origin} | — |"
    )

with open(SCHEMA_PATH, 'w', encoding='utf-8') as f:
    f.write('\n'.join(schema_lines))

print(f"    Schema: {SCHEMA_PATH}")

# Resumo Final
print(f"\n{'─' * 70}")
print(f"\n  RESUMO FINAL")
print(f"{'─' * 70}")
print(f"    Linhas (Pedidos):      {len(df):>12,}")
print(f"    Colunas:               {len(df.columns):>12}")
print(f"    Receita Total:         R$ {revenue_unified:>10,.2f}")
print(f"    Clientes únicos:       {df['customer_unique_id'].nunique():>12,}")
print(f"    Tamanho CSV:           {csv_size:>11.1f} MB")

print(f"\n{'=' * 70}")
print("  Pipeline Abordagem 1 concluído com sucesso!")
print(f"{'=' * 70}\n")
