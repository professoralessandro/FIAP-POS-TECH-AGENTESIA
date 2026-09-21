# Schema do DataFrame Unificado Olist — Abordagem 1

> **Gerado em:** 2026-07-20 19:00:50

> **Granularidade:** Pedido (Order-level)

> **Linhas (pedidos):** 99,441 | **Colunas:** 52


## ⚙️ Decisões Aplicadas nesta Abordagem:
- **Geolocalização:** Integrada com mediana por CEP para clientes e vendedores.
- **Produtos sem Categoria:** Substituídos por `'sem_categoria'`.
- **Reviews:** Deduplicados por `order_id` mantendo o primeiro registro.
- **Granularidade:** Agregada no nível de pedido (`order_id`). Itens e valores financeiros somados.
- **Formato de Saída:** CSV.

## 📋 Dicionário de Colunas:

| # | Coluna | Tipo | Nulos | % Nulos | Origem | Descrição |
|---|---|---|---:|---:|---|---|
| 1 | `order_id` | object | 0 | 0.0% | orders | — |
| 2 | `customer_id` | object | 0 | 0.0% | orders | — |
| 3 | `order_status` | object | 0 | 0.0% | orders | — |
| 4 | `order_purchase_timestamp` | datetime64[ns] | 0 | 0.0% | orders | — |
| 5 | `order_approved_at` | datetime64[ns] | 160 | 0.2% | orders | — |
| 6 | `order_delivered_carrier_date` | datetime64[ns] | 1,783 | 1.8% | orders | — |
| 7 | `order_delivered_customer_date` | datetime64[ns] | 2,965 | 3.0% | orders | — |
| 8 | `order_estimated_delivery_date` | datetime64[ns] | 0 | 0.0% | orders | — |
| 9 | `price_total` | float64 | 775 | 0.8% | order_items (agg) | — |
| 10 | `freight_total` | float64 | 775 | 0.8% | order_items (agg) | — |
| 11 | `items_count` | float64 | 775 | 0.8% | order_items (agg) | — |
| 12 | `unique_products_count` | float64 | 775 | 0.8% | order_items (agg) | — |
| 13 | `unique_sellers_count` | float64 | 775 | 0.8% | order_items (agg) | — |
| 14 | `main_product_id` | object | 775 | 0.8% | order_items (agg) | — |
| 15 | `main_seller_id` | object | 775 | 0.8% | order_items (agg) | — |
| 16 | `customer_unique_id` | object | 0 | 0.0% | customers | — |
| 17 | `customer_zip_code_prefix` | int64 | 0 | 0.0% | customers | — |
| 18 | `customer_city` | object | 0 | 0.0% | customers | — |
| 19 | `customer_state` | object | 0 | 0.0% | customers | — |
| 20 | `product_category_name` | object | 775 | 0.8% | products | — |
| 21 | `product_weight_g` | float64 | 791 | 0.8% | products | — |
| 22 | `product_length_cm` | float64 | 791 | 0.8% | products | — |
| 23 | `product_height_cm` | float64 | 791 | 0.8% | products | — |
| 24 | `product_width_cm` | float64 | 791 | 0.8% | products | — |
| 25 | `product_category_name_english` | object | 796 | 0.8% | categories | — |
| 26 | `seller_zip_code_prefix` | float64 | 775 | 0.8% | sellers | — |
| 27 | `seller_city` | object | 775 | 0.8% | sellers | — |
| 28 | `seller_state` | object | 775 | 0.8% | sellers | — |
| 29 | `review_id` | object | 768 | 0.8% | reviews | — |
| 30 | `review_score` | float64 | 768 | 0.8% | reviews | — |
| 31 | `review_comment_title` | object | 87,890 | 88.4% | reviews | — |
| 32 | `review_comment_message` | object | 58,656 | 59.0% | reviews | — |
| 33 | `review_creation_date` | datetime64[ns] | 768 | 0.8% | reviews | — |
| 34 | `review_answer_timestamp` | datetime64[ns] | 768 | 0.8% | reviews | — |
| 35 | `payment_value_total` | float64 | 1 | 0.0% | payments (agg) | — |
| 36 | `payment_installments_max` | float64 | 1 | 0.0% | payments (agg) | — |
| 37 | `payment_type_main` | object | 1 | 0.0% | payments (agg) | — |
| 38 | `n_payment_methods` | float64 | 1 | 0.0% | payments (agg) | — |
| 39 | `customer_lat` | float64 | 278 | 0.3% | geolocation (agg) | — |
| 40 | `customer_lng` | float64 | 278 | 0.3% | geolocation (agg) | — |
| 41 | `seller_lat` | float64 | 993 | 1.0% | geolocation (agg) | — |
| 42 | `seller_lng` | float64 | 993 | 1.0% | geolocation (agg) | — |
| 43 | `lead_time_days` | float64 | 2,965 | 3.0% | **DERIVADA** | — |
| 44 | `delay_days` | float64 | 2,965 | 3.0% | **DERIVADA** | — |
| 45 | `is_late` | boolean | 0 | 0.0% | **DERIVADA** | — |
| 46 | `approval_time_hours` | float64 | 160 | 0.2% | **DERIVADA** | — |
| 47 | `purchase_year_month` | object | 0 | 0.0% | **DERIVADA** | — |
| 48 | `purchase_dow` | int32 | 0 | 0.0% | **DERIVADA** | — |
| 49 | `purchase_hour` | int32 | 0 | 0.0% | **DERIVADA** | — |
| 50 | `freight_ratio` | float64 | 775 | 0.8% | **DERIVADA** | — |
| 51 | `has_review_text` | bool | 0 | 0.0% | **DERIVADA** | — |
| 52 | `is_cross_state` | bool | 0 | 0.0% | **DERIVADA** | — |