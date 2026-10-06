# MarketMind AI: Collaborative Filtering Recommendations

## Milestone 3, Day 1-2

This milestone sets up basic customer-product collaborative filtering from the existing processed Sales and Customer data. It does not implement Association Rule Mining, Apriori, support, confidence, lift, cross-sell/upsell logic, churn, anomaly detection, frontend panels, or new authentication/RBAC.

## Input data

The implementation uses:

- `data/processed/sales/cleaned_sales.csv`
- `data/processed/customers/cleaned_customers.csv`

The Sales fields used are `customer_id`, `product_name`, and `quantity`. The existing cleaned Sales file is read only; raw datasets are not modified.

## Customer-product matrix

The matrix has:

- Rows: `customer_id`
- Columns: `product_name`
- Values: summed `quantity` purchased by each customer for each product
- Missing customer-product values: filled with `0`

All processed customer IDs are included so a valid customer with no purchase history can remain represented with a zero row. Repeated purchases for the same customer and product are aggregated using sum.

Actual matrix statistics:

- Customers: **300**
- Products: **24**
- Matrix shape: **(300, 24)**
- Similarity matrix shape: **(300, 300)**
- Customers with at least one generated recommendation: **299**
- Recommendation rows written: **863**

## Collaborative filtering approach

The model is implemented in `backend/models/recommendation/collaborative_filtering.py` and the orchestration service is `backend/services/recommendation_service.py`.

1. Build the customer-product quantity matrix.
2. Calculate customer-to-customer similarity with `sklearn.metrics.pairwise.cosine_similarity`.
3. Exclude the target customer from the neighbor list.
4. Find similar customers by descending cosine similarity.
5. Collect products purchased by those customers.
6. Remove products already purchased by the target customer.
7. Score remaining products by similarity-weighted purchased quantity.
8. Sort by score and product name and return up to `top_n` products.

The implementation uses deterministic sorting for ties and does not use fabricated products or scores.

## Actual recommendation example

The service selected the first actual customer in the processed customer index: **`C0001`**.

Products already purchased by `C0001` included Notebook, Ballpoint Pen Pack, Cotton T-Shirt, Coffee Beans, Webcam, and other products in the generated Sales history.

Most similar customers:

| Customer | Cosine similarity |
| -------- | ----------------: |
| `C0219`  |          0.807576 |
| `C0188`  |          0.760044 |
| `C0221`  |          0.742318 |
| `C0187`  |          0.736673 |
| `C0203`  |          0.731618 |

Top-3 recommendations:

| Rank | Recommended product | Recommendation score | Supporting customers |
| ---: | ------------------- | -------------------: | -------------------: |
|    1 | Wireless Mouse      |           895.131565 |                  273 |
|    2 | Printer Paper       |           710.776905 |                  261 |
|    3 | LED Bulb Pack       |           605.677943 |                  241 |

These values are the actual output of the current processed dataset and deterministic recommender run.

## Edge-case handling

- **Unknown `customer_id`:** raises a clear `KeyError` rather than fabricating a profile or recommendation.
- **Customer with no purchase history:** returns an empty recommendation list because there is no target preference vector to compare.
- **Similar customers have no new products:** returns an empty list after already-purchased products are removed.
- **Fewer than `top_n` possible products:** returns only the available products.
- **`top_n` less than one:** returns an empty list.

## Generated outputs

- `data/processed/recommendations/customer_product_matrix.csv`
- `data/processed/recommendations/customer_similarity.csv`
- `data/processed/recommendations/collaborative_recommendations.csv`

The recommendation output contains `customer_id`, `rank`, `recommended_product`, `recommendation_score`, and `supporting_customer_count`.

## Run command

From the repository root:

```powershell
.venv\Scripts\python.exe -m backend.services.recommendation_service
```

The service prints the processed customer/product counts, selected actual customer, purchased products, most similar customers, recommendations, and output locations.
