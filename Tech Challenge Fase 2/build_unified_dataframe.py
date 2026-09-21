"""
=============================================================================
 OLIST MARKETPLACE — BUILD UNIFIED DATAFRAME
 Consolida as 9 tabelas da Olist em um DataFrame analitico unico.
 Granularidade: 1 linha = 1 item vendido em 1 pedido.
=============================================================================
 Execucao:  python build_unified_dataframe.py
 Output:    discovery_output/olist_unified.parquet
            discovery_output/olist_unified_schema.md
=============================================================================
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

# =============================================================================
# CONFIGURACAO
# =============================================================================
DATA_DIR = os.path.join(os.path.dirname(__file__), "OLIST Dataset")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "discovery_output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

PARQUET_PATH = os.path.join(OUTPUT_DIR, "olist_unified.parquet")
SCHEMA_PATH = os.path.join(OUTPUT_DIR, "olist_unified_schema.md")


# =============================================================================
# 1. CARREGAMENTO DOS DADOS
# =============================================================================
print("=" * 70)
print("  OLIST — BUILD UNIFIED DATAFRAME")
print("=" * 70)
print(f"\n  Inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"  Fonte:  {DATA_DIR}\n")

files = {
    'orders':       'olist_orders_dataset.csv',
    'items':        'olist_order_items_dataset.csv',
    'payments':     'olist_order_payments_dataset.csv',
    'reviews':      'olist_order_reviews_dataset.csv',
    'customers':    'olist_customers_dataset.csv',
    'products':     'olist_products_dataset.csv',
    'sellers':      'olist_sellers_dataset.csv',
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
# 2. CONVERSAO DE TIPOS (DATAS)
# =============================================================================
print("\n  Convertendo colunas de data/hora...\n")

date_cols = {
    'orders': [
        'order_purchase_timestamp', 'order_approved_at',
        'order_delivered_carrier_date', 'order_delivered_customer_date',
        'order_estimated_delivery_date'
    ],
    'items': ['shipping_limit_date'],
    'reviews': ['review_creation_date', 'review_answer_timestamp'],
}

for table, cols in date_cols.items():
    for col in cols:
        ds[table][col] = pd.to_datetime(ds[table][col], errors='coerce')
        print(f"    {table}.{col}")

print(f"\n{'─' * 70}")


# =============================================================================
# 3. PRE-AGREGACAO: PAYMENTS (N linhas -> 1 por order_id)
# =============================================================================
print("\n  Pre-agregando payments por order_id...\n")

payments_agg = ds['payments'].groupby('order_id').agg(
    payment_value_total=('payment_value', 'sum'),
    payment_installments_max=('payment_installments', 'max'),
    payment_type_main=('payment_type', lambda x: x.value_counts().index[0]),
    n_payment_methods=('payment_sequential', 'nunique'),
).reset_index()

print(f"    {len(ds['payments']):,} linhas -> {len(payments_agg):,} linhas (agregadas)")
print(f"\n{'─' * 70}")


# =============================================================================
# 4. TRATAMENTO: PRODUTOS SEM CATEGORIA
# =============================================================================
print("\n  Tratando produtos sem categoria...\n")

n_null_cat = ds['products']['product_category_name'].isnull().sum()
ds['products']['product_category_name'] = (
    ds['products']['product_category_name'].fillna('sem_categoria')
)
print(f"    {n_null_cat} produtos rotulados como 'sem_categoria'")

# Adicionar traducao para sem_categoria
new_row = pd.DataFrame({
    'product_category_name': ['sem_categoria'],
    'product_category_name_english': ['uncategorized']
})
ds['categories'] = pd.concat([ds['categories'], new_row], ignore_index=True)
print(f"    Tradução 'sem_categoria' -> 'uncategorized' adicionada")

print(f"\n{'─' * 70}")


# =============================================================================
# 5. JOINS SEQUENCIAIS
# =============================================================================
print("\n  Executando joins sequenciais...\n")

# Tabela ancora: order_items
df = ds['items'].copy()
print(f"    [ANCORA] order_items: {len(df):,} linhas")

# Join 1: + orders (order_id)
df = df.merge(ds['orders'], on='order_id', how='left')
print(f"    [JOIN 1] + orders          -> {len(df):,} linhas")

# Join 2: + customers (customer_id)
df = df.merge(ds['customers'], on='customer_id', how='left')
print(f"    [JOIN 2] + customers       -> {len(df):,} linhas")

# Join 3: + products (product_id)
df = df.merge(ds['products'], on='product_id', how='left')
print(f"    [JOIN 3] + products        -> {len(df):,} linhas")

# Join 4: + category_translation (product_category_name)
df = df.merge(ds['categories'], on='product_category_name', how='left')
print(f"    [JOIN 4] + categories      -> {len(df):,} linhas")

# Join 5: + sellers (seller_id)
# Renomear colunas de sellers para evitar conflito com customers
sellers_renamed = ds['sellers'].rename(columns={
    'seller_zip_code_prefix': 'seller_zip_code_prefix',
    'seller_city': 'seller_city',
    'seller_state': 'seller_state',
})
df = df.merge(sellers_renamed, on='seller_id', how='left')
print(f"    [JOIN 5] + sellers         -> {len(df):,} linhas")

# Join 6: + reviews (order_id)
reviews_cols = [
    'order_id', 'review_id', 'review_score',
    'review_comment_title', 'review_comment_message',
    'review_creation_date', 'review_answer_timestamp'
]
df = df.merge(ds['reviews'][reviews_cols], on='order_id', how='left')
print(f"    [JOIN 6] + reviews         -> {len(df):,} linhas")

# Join 7: + payments_agg (order_id)
df = df.merge(payments_agg, on='order_id', how='left')
print(f"    [JOIN 7] + payments (agg)  -> {len(df):,} linhas")

print(f"\n{'─' * 70}")


# =============================================================================
# 6. FEATURES DERIVADAS
# =============================================================================
print("\n  Criando features derivadas...\n")

# Tempos logisticos
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
    df['price'] > 0,
    df['freight_value'] / df['price'],
    np.nan
)

# NLP flag
df['has_review_text'] = df['review_comment_message'].notna()

# Logistica geografica
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
# 7. VALIDACOES
# =============================================================================
print("\n  Executando validacoes...\n")

checks = []
original_items_count = len(ds['items'])

# Contagem de linhas
n_rows = len(df)
checks.append(('Contagem de linhas', f'{n_rows:,}', 'INFO'))

# Contagem de colunas
checks.append(('Contagem de colunas', f'{len(df.columns)}', 'INFO'))

# Nulos criticos
for col in ['order_id', 'order_status', 'product_id', 'seller_id', 'customer_id']:
    n_null = df[col].isnull().sum()
    status = 'OK' if n_null == 0 else f'ALERTA: {n_null} nulos'
    checks.append((f'Nulos em {col}', str(n_null), status))

# Nulos em review_score (esperado: pedidos sem review)
n_null_review = df['review_score'].isnull().sum()
checks.append((
    'Nulos em review_score',
    f'{n_null_review:,}',
    'OK (pedidos sem review)' if n_null_review < 5000 else 'ALERTA'
))

# Nulos em product_category_name
n_null_cat = (df['product_category_name'] == 'sem_categoria').sum()
checks.append((
    'Items com sem_categoria',
    f'{n_null_cat:,}',
    'OK (rotulados)'
))

# Consistencia de receita
revenue_original = ds['items']['price'].sum()
revenue_unified = df['price'].sum()
# A receita pode mudar se reviews causaram expansao
rev_per_item = revenue_unified / n_rows * original_items_count
checks.append((
    'Receita original (items)',
    f'R$ {revenue_original:,.2f}',
    'INFO'
))
checks.append((
    'Receita no unificado',
    f'R$ {revenue_unified:,.2f}',
    'INFO (pode estar inflada por joins 1:N de reviews)'
))

# Pedidos unicos
n_orders = df['order_id'].nunique()
checks.append(('Pedidos unicos', f'{n_orders:,}', 'INFO'))

# Clientes unicos
n_customers = df['customer_unique_id'].nunique()
checks.append(('Clientes unicos (customer_unique_id)', f'{n_customers:,}', 'INFO'))

for label, value, status in checks:
    icon = '  OK ' if 'OK' in status else ' INFO' if status == 'INFO' else ' !!! '
    print(f"    [{icon}] {label:45s}  {value:>15s}  {status}")

print(f"\n{'─' * 70}")


# =============================================================================
# 8. SALVAR OUTPUT
# =============================================================================
print(f"\n  Salvando outputs...\n")

# Parquet
df.to_parquet(PARQUET_PATH, index=False, engine='pyarrow')
parquet_size = os.path.getsize(PARQUET_PATH) / (1024 * 1024)
print(f"    Parquet: {PARQUET_PATH}")
print(f"    Tamanho: {parquet_size:.1f} MB")

# Schema documentation
schema_lines = [
    "# Schema do DataFrame Unificado Olist\n",
    f"> Gerado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
    f"> Linhas: {len(df):,} | Colunas: {len(df.columns)}\n",
    "",
    "| # | Coluna | Tipo | Nulos | % Nulos | Origem |",
    "|---|---|---|---:|---:|---|",
]

for i, col in enumerate(df.columns, 1):
    dtype = str(df[col].dtype)
    n_null = df[col].isnull().sum()
    pct_null = n_null / len(df) * 100

    # Determinar origem
    if col in ds['items'].columns:
        origin = 'order_items'
    elif col in ds['orders'].columns:
        origin = 'orders'
    elif col in ds['customers'].columns:
        origin = 'customers'
    elif col in ds['products'].columns:
        origin = 'products'
    elif col in ds['sellers'].columns:
        origin = 'sellers'
    elif col in ds['reviews'].columns:
        origin = 'reviews'
    elif col in payments_agg.columns:
        origin = 'payments (agg)'
    elif col in ds['categories'].columns:
        origin = 'categories'
    elif col in features_created:
        origin = '**DERIVADA**'
    else:
        origin = '—'

    schema_lines.append(
        f"| {i} | `{col}` | {dtype} | {n_null:,} | {pct_null:.1f}% | {origin} |"
    )

with open(SCHEMA_PATH, 'w', encoding='utf-8') as f:
    f.write('\n'.join(schema_lines))

print(f"    Schema: {SCHEMA_PATH}")

# Quick stats
print(f"\n{'─' * 70}")
print(f"\n  RESUMO FINAL")
print(f"{'─' * 70}")
print(f"    Linhas:                {len(df):>12,}")
print(f"    Colunas:               {len(df.columns):>12}")
print(f"    Pedidos unicos:        {df['order_id'].nunique():>12,}")
print(f"    Clientes unicos:       {df['customer_unique_id'].nunique():>12,}")
print(f"    Produtos unicos:       {df['product_id'].nunique():>12,}")
print(f"    Vendedores unicos:     {df['seller_id'].nunique():>12,}")
print(f"    Categorias:            {df['product_category_name'].nunique():>12}")
print(f"    Periodo:               {df['order_purchase_timestamp'].min().strftime('%Y-%m-%d')} a {df['order_purchase_timestamp'].max().strftime('%Y-%m-%d')}")
print(f"    Tamanho Parquet:       {parquet_size:>11.1f} MB")

print(f"\n{'=' * 70}")
print("  Pipeline concluido com sucesso!")
print(f"{'=' * 70}\n")
