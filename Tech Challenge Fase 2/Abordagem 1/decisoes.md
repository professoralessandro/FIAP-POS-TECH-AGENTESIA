# 📑 Decisões Arquiteturais — Abordagem 1

Este documento registra as decisões tomadas para a construção do DataFrame unificado na pasta `abordagem 1`.

---

## ⚙️ Configurações Escolhidas

### 1. Geolocalização (Opção B — Integrada)
- **Estratégia:** As coordenadas (latitude e longitude) serão incorporadas diretamente no DataFrame unificado.
- **Implementação:** O dataset `olist_geolocation_dataset.csv` será agregado pela mediana das coordenadas agrupadas por CEP (`zip_code_prefix`). Isso evita a explosão de registros (já que há muitos pontos por CEP) e anexa a localização estimada para clientes (`customer_lat`, `customer_lng`) e vendedores (`seller_lat`, `seller_lng`).

### 2. Tratamento de Produtos sem Categoria (Opção D — Rotulação)
- **Estratégia:** Produtos com valores ausentes no campo de categoria serão rotulados explicitamente como `"sem_categoria"` no idioma original, e `"uncategorized"` na coluna traduzida para o inglês.

### 3. Reviews Duplicados (Deduplicação no Join)
- **Estratégia:** Remoção de duplicatas de reviews baseando-se no `order_id` antes de efetuar o merge, garantindo que cada pedido tenha no máximo uma avaliação associada no dataset final.

### 4. Formato de Saída (CSV)
- **Estratégia:** O arquivo final será exportado no formato texto delimitado por vírgulas (CSV) para facilitar a visualização direta e compatibilidade rápida com outras ferramentas de BI ou planilhas.
- **Destino:** `abordagem 1/olist_unified.csv`

### 5. Granularidade (Nível Pedido — 99k linhas)
- **Estratégia:** A granularidade do DataFrame será de **um registro por pedido** (aprox. 99.441 linhas).
- **Implementação:** Os itens contidos em `order_items` serão agregados por `order_id`. Valores financeiros (`price`, `freight_value`) serão somados, a contagem de itens será computada e utilizaremos o ID do produto principal (primeiro item) e vendedor principal para trazer seus respectivos metadados.
