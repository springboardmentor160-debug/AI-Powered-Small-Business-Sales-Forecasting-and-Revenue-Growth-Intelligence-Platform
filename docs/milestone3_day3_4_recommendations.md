# MarketMind AI: Association Rules and Combined Recommendations

## Milestone 3, Day 3-4

This milestone adds Apriori association-rule mining and combines it with the existing customer-based collaborative filtering recommender. The implementation uses only the actual processed Sales data and preserves the Day 1-2 collaborative-filtering outputs.

## Actual basket inspection

The processed source is `data/processed/sales/cleaned_sales.csv`, using the project schema and `transaction_id` as the basket identifier.

Actual inspection found:

- Sales rows: **12,000**
- Unique transactions: **12,000**
- Multi-product transactions: **0**
- Maximum products in one transaction: **1**
- Product rows per transaction: every transaction contains exactly one product
- Unique products: **24**

The handout's multi-product basket logic cannot produce genuine product combinations from this dataset. No multi-product baskets were invented. The transaction basket still follows the required format: one row per actual `transaction_id`, one product column per `product_name`, and a binary `1`/`0` presence value.

## Apriori approach

The model is implemented in `backend/models/recommendation/association_rules.py` and integrated by `backend/services/recommendation_service.py`.

- Frequent itemsets are generated with `mlxtend.frequent_patterns.apriori`.
- `min_support` is `0.01`.
- Rules use `min_confidence` of `0.1`.
- Rules are retained only when `lift > 1`, which represents a positive association.
- Rule columns are `antecedents`, `consequents`, `support`, `confidence`, and `lift`.
- Deterministic sorting is used for itemsets and rules.

Actual Apriori results:

- Transaction-product matrix: **(12,000, 24)**
- Frequent itemsets: **24** singleton itemsets
- Association rules: **0**
- Cross-sell suggestions: **0**
- Upsell opportunities: **0**

Because every actual basket has one product, no two-product itemset can reach support and no association rule can be calculated from a genuine product combination. Consequently, the empty rule, cross-sell, and upsell outputs are the correct factual result for the current data.

## Combined recommendation approach

The existing collaborative-filtering implementation remains the source of personalized recommendations:

1. Build the customer-product quantity matrix.
2. Calculate customer similarity with cosine similarity.
3. Find similar customers and exclude the target customer.
4. Aggregate products purchased by similar customers.
5. Remove products already purchased by the target customer.
6. Rank recommendations using similarity-weighted quantity.

Association-rule results are combined when valid rules exist. In the current dataset, there are no valid rules, so the combined output contains the existing personalized collaborative recommendations only. No fake cross-sell or upsell values are added.

## Actual recommendation example

The service used actual customer **`C0001`**:

- Most similar customers: `C0219` (0.807576), `C0188` (0.760044), `C0221` (0.742318), `C0187` (0.736673), `C0203` (0.731618).
- Personalized recommendations:
  1. **Wireless Mouse** — score `895.131565`, supported by 273 similar customers.
  2. **Printer Paper** — score `710.776905`, supported by 261 similar customers.
  3. **LED Bulb Pack** — score `605.677943`, supported by 241 similar customers.

These recommendations exclude products already purchased by `C0001`.

## Generated outputs

- `data/processed/recommendations/transaction_product_matrix.csv`
- `data/processed/recommendations/frequent_itemsets.csv`
- `data/processed/recommendations/association_rules.csv`
- `data/processed/recommendations/cross_sell_recommendations.csv`
- `data/processed/recommendations/upsell_opportunities.csv`
- `data/processed/recommendations/combined_recommendations.csv`

The existing Day 1-2 outputs are also regenerated and preserved:

- `data/processed/recommendations/customer_product_matrix.csv`
- `data/processed/recommendations/customer_similarity.csv`
- `data/processed/recommendations/collaborative_recommendations.csv`

## Verification

- Confirmed `transaction_id` has no multi-product baskets before implementing Apriori.
- Verified actual basket shape `(12,000, 24)`.
- Verified 24 singleton frequent itemsets and zero association rules.
- Verified association-rule output columns include `antecedents`, `consequents`, `support`, `confidence`, and `lift`.
- Verified cross-sell and upsell outputs are empty rather than fabricated.
- Verified the existing collaborative-filtering output remains 863 rows for 299 customers.
- Verified raw/processed Sales input is unchanged.
- Verified all recommendation outputs are deterministic on rerun.

Run from the repository root:

```powershell
.venv\Scripts\python.exe -m backend.services.recommendation_service
```
