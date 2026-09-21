# 🔧 Análise de Tratamento de Dados — Prós e Contras

> **Objetivo:** Subsidiar a tomada de decisão antes de executar o tratamento dos dois problemas de qualidade identificados no Discovery.

---

## Problema 1: 610 Produtos sem Categoria

### Diagnóstico Factual

| Métrica | Valor |
|---|---|
| Produtos sem categoria | **610** de 32.951 (1,85%) |
| Itens vendidos desses produtos | 1.603 (1,42% do total) |
| Pedidos envolvidos | 1.451 |
| Receita (price) | R$ 179.535 (**1,32%** do GMV) |
| Reviews associados | 1.448 (score médio: **3,91**) |
| Vendedores envolvidos | 257 |

**Padrão observado:** Os 610 produtos têm **todos os campos de catálogo nulos** (`product_name_lenght`, `product_description_lenght`, `product_photos_qty`) mas **possuem dimensões físicas** (peso, comprimento, altura, largura) — exceto 1 produto. Isso sugere cadastro incompleto (vendedor preencheu dados de envio mas não concluiu o catálogo).

---

### Abordagens de Tratamento

#### Opção A — Criar categoria "sem_categoria" / "unknown"

Atribui um rótulo explícito (ex: `"sem_categoria"`) no campo `product_category_name`.

| | Detalhe |
|---|---|
| ✅ **Prós** | Preserva 100% dos registros. Nenhuma perda de receita ou reviews. Transparente — a ausência vira uma categoria visível. Simples de implementar. |
| ❌ **Contras** | Polui análises de "Top Categorias" e dashboards. A categoria "unknown" pode acabar aparecendo em rankings. Não resolve o problema real (não sabemos *o que* são esses produtos). |
| 🎯 **Quando usar** | Quando o foco é **volume geral** (KPIs, séries temporais, NPS, logística) e a categoria não é a dimensão principal de análise. |

#### Opção B — Remover os 610 produtos (e itens/pedidos associados)

Exclui os registros do pipeline de análise. 

| | Detalhe |
|---|---|
| ✅ **Prós** | Dados limpos — toda análise por categoria fica 100% confiável. Elimina o "ruído" visual. |
| ❌ **Contras** | Perde **1,32% da receita** (R$ 179k), 1.451 pedidos e 1.448 reviews. Pode distorcer ligeiramente métricas globais. Se a análise for de satisfação geral, perder 1.448 reviews é relevante. |
| 🎯 **Quando usar** | Quando a análise é **exclusivamente por categoria** e não se quer nenhum "lixo" nos gráficos. |

#### Opção C — Inferir categoria via dimensões físicas (peso + tamanho)

Treinar um classificador simples (ex: KNN, Random Forest) usando as dimensões como features para predizer a categoria.

| | Detalhe |
|---|---|
| ✅ **Prós** | Preserva os registros *e* preenche a categoria. Demonstra técnica avançada (feature engineering + ML) — bom para o Tech Challenge. |
| ❌ **Contras** | Complexidade alta para um ganho de 1,32%. As dimensões sozinhas são fracas para distinguir categorias (um livro e um tablet podem ter peso similar). Risco de introduzir erro sistemático. Precisa validar acurácia. |
| 🎯 **Quando usar** | Se o projeto tiver um viés acadêmico e você quiser demonstrar ML aplicado a data quality. |

#### Opção D — Abordagem Híbrida ⭐ (Recomendada)

Manter os registros, rotular como `"sem_categoria"`, mas **filtrar condicionalmente** nas análises:
- **Análises por categoria** (top categorias, receita por segmento): filtrar `sem_categoria` fora
- **Análises globais** (KPIs, NPS, logística, temporal): manter tudo

| | Detalhe |
|---|---|
| ✅ **Prós** | Zero perda de dados. Gráficos de categoria ficam limpos. KPIs globais ficam precisos. Implementação simples. Decisão reversível. |
| ❌ **Contras** | Requer disciplina de sempre lembrar o filtro. Precisa documentar claramente o critério. |
| 🎯 **Quando usar** | Na maioria dos cenários reais — é a abordagem mais pragmática e defensável. |

---

## Problema 2: 814 Review_IDs Duplicados

### Diagnóstico Factual

| Métrica | Valor |
|---|---|
| review_ids com duplicata | **789** IDs distintos |
| Linhas totais envolvidas | 1.603 |
| Linhas "extras" | 814 |
| Distribuição | 764 aparecem **2x**, 25 aparecem **3x** |

**Descoberta crucial:** Em **100% da amostra analisada** (100 review_ids):
- Os order_ids são **DIFERENTES** em cada ocorrência
- O conteúdo (score + mensagem) é **IDÊNTICO**

> **Interpretação:** Um mesmo cliente fez múltiplos pedidos e enviou reviews com o **mesmo conteúdo copiado** (ou o sistema da Olist reaplicou a mesma avaliação). O `review_id` é um hash do conteúdo, não do pedido. Isso faz sentido no modelo de marketplace.

| Pedidos envolvidos | 1.412 |
|---|---|
| Receita | R$ 152.549 (1,12% do total) |

---

### Abordagens de Tratamento

#### Opção A — Não fazer nada (manter como está)

| | Detalhe |
|---|---|
| ✅ **Prós** | Nenhum risco de perda de dados. Cada pedido mantém sua avaliação associada. Se a relação é 1 review : 1 order, mesmo com review_id repetido, a granularidade está correta. |
| ❌ **Contras** | O `review_id` não funciona como PK. Se alguém fizer `reviews.drop_duplicates('review_id')`, perde reviews válidos. Pode inflar métricas de NLP se o mesmo texto for contado múltiplas vezes. |
| 🎯 **Quando usar** | Se a análise é centrada no **pedido** (join por `order_id`) e o `review_id` nunca é usado como chave. |

#### Opção B — Deduplicar por review_id (manter primeiro)

Remove linhas "extras" com `reviews.drop_duplicates(subset='review_id', keep='first')`.

| | Detalhe |
|---|---|
| ✅ **Prós** | `review_id` volta a ser PK válida. Análises de NLP ficam limpas (sem duplicação de texto). |
| ❌ **Contras** | **Perde 814 relações pedido↔review** legítimas. Se a análise é "review score por pedido", esses pedidos ficam sem avaliação. Distorce a taxa de review por pedido. |
| 🎯 **Quando usar** | Quando a análise é centrada no **conteúdo do review** (NLP, topic modeling, word clouds). |

#### Opção C — Deduplicar por (review_id + order_id) como chave composta

Mantém todas as linhas mas trata a PK como **composta** (`review_id`, `order_id`).

| | Detalhe |
|---|---|
| ✅ **Prós** | Zero perda de dados. Cada pedido mantém seu review. `review_id` passa a ser "ID de conteúdo" e `order_id` mantém a relação transacional. Verifica se existem duplicatas *reais* (mesmo review_id + mesmo order_id). |
| ❌ **Contras** | Requer ajuste conceitual no ERD (PK composta). Análises de contagem de "reviews únicos" precisam ser feitas com cuidado. |
| 🎯 **Quando usar** | Quando se quer preservar a relação completa pedido↔review e os dados de NLP. |

#### Opção D — Abordagem contextual ⭐ (Recomendada)

Tratar diferente dependendo do tipo de análise:

| Análise | Tratamento |
|---|---|
| **KPIs / Score médio / NPS** | Usar todas as 99.224 linhas (join por `order_id`, sem deduplicar) |
| **NLP / Análise de texto** | Deduplicar por `review_id` para não contar o mesmo texto 2-3x |
| **Contagem de reviews** | Contar por `order_id` (1 review por pedido) |

| | Detalhe |
|---|---|
| ✅ **Prós** | Tratamento correto para cada contexto. Nenhuma perda desnecessária. Demonstra maturidade analítica. |
| ❌ **Contras** | Mais trabalho de implementação. Precisa documentar qual filtro foi usado em cada análise. |

---

## 📊 Resumo Comparativo

### Produtos sem Categoria (610)

| Opção | Perda de dados | Complexidade | Risco | Recomendação |
|---|---|---|---|---|
| A — "sem_categoria" | Nenhuma | ⬤○○ Baixa | ⬤○○ Baixo | ✅ Bom |
| B — Remover | 1,32% receita | ⬤○○ Baixa | ⬤⬤○ Médio | ⚠️ Aceitável |
| C — Inferir via ML | Nenhuma | ⬤⬤⬤ Alta | ⬤⬤⬤ Alto | ❌ Custo/benefício ruim |
| **D — Híbrida** | **Nenhuma** | **⬤○○ Baixa** | **⬤○○ Baixo** | **⭐ Recomendada** |

### Reviews Duplicados (814)

| Opção | Perda de dados | Complexidade | Risco | Recomendação |
|---|---|---|---|---|
| A — Não mexer | Nenhuma | ⬤○○ Nula | ⬤⬤○ Médio | ⚠️ Aceitável |
| B — Drop duplicates | 814 relações | ⬤○○ Baixa | ⬤⬤○ Médio | ⚠️ Apenas p/ NLP |
| C — Chave composta | Nenhuma | ⬤⬤○ Média | ⬤○○ Baixo | ✅ Bom |
| **D — Contextual** | **Nenhuma** | **⬤⬤○ Média** | **⬤○○ Baixo** | **⭐ Recomendada** |

---

> [!TIP]
> **Minha recomendação geral:** Opção D para ambos os problemas. Impacto total é pequeno (~1,3% da receita cada), então o importante é **não perder dados** e **documentar** o critério usado. Isso é mais defensável numa apresentação do que qualquer abordagem de "remover e ignorar".
