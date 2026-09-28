# MarketMind AI: Hierarchical Customer Segmentation

## Milestone 2, Day 3-4

This milestone extends the Day 1-2 customer segmentation setup with hierarchical clustering and behavior-based segment names. The existing K-Means implementation remains the baseline and its `cluster` output is preserved.

## Data and features

The implementation reuses:

- `data/processed/sales/cleaned_sales.csv`
- `data/processed/customers/cleaned_customers.csv`

Customer-level features are unchanged:

- **`purchase_frequency`:** Number of sales transaction records for the customer.
- **`purchase_value`:** Sum of the customer's `total_amount` values.
- **`customer_activity`:** Number of distinct calendar purchase dates.

Customers without transactions remain supported by the existing left join and receive zero-valued behavioral features. Raw data is not modified.

## Method

1. Build the customer-level features using the existing `segmentation_service.py` implementation.
2. Apply the existing `log1p` transformation and `StandardScaler` preprocessing.
3. Run the existing K-Means model and preserve its cluster labels and elbow diagnostics.
4. Use the K-Means-selected cluster count as the hierarchical clustering count.
5. Apply scikit-learn Agglomerative Clustering with Ward linkage to the same standardized features.
6. Analyze the hierarchical cluster means before assigning business-friendly names.
7. Save both cluster labels and the segment name in the processed output.

The initial K-Means elbow selection remains **3 clusters**. The hierarchical model uses the same `k=3` so the two methods can be compared on the same customer feature space. K-Means uses `random_state=42` and `n_init=10`; Ward hierarchical clustering is deterministic for these inputs.

## Baseline K-Means results

| K-Means cluster | Customers |
| --------------: | --------: |
|               0 |       110 |
|               1 |       138 |
|               2 |        52 |

## Hierarchical behavior analysis

The following means were calculated from the actual output features before naming the clusters:

| Hierarchical cluster | Segment name           | Customers | Mean purchase frequency | Mean purchase value | Mean customer activity |
| -------------------: | ---------------------- | --------: | ----------------------: | ------------------: | ---------------------: |
|                    0 | Regular Customers      |       197 |                   40.15 |             1595.28 |                  39.45 |
|                    1 | Low Activity Customers |        52 |                   30.96 |             1199.44 |                  30.48 |
|                    2 | High Value Customers   |        51 |                   48.65 |             2075.60 |                  47.78 |

The names are based on these observed patterns: Hierarchical cluster 2 has the highest average purchase value, frequency, and activity; cluster 1 has the lowest averages; and cluster 0 is intermediate across the three features.

## Actual hierarchical results

- Customers processed: **300**
- Hierarchical cluster counts: **197**, **52**, and **51**
- Segment counts:
  - **Regular Customers:** 197
  - **Low Activity Customers:** 52
  - **High Value Customers:** 51

## Output

The combined output is saved to:

`data/processed/segments/customer_segments.csv`

It contains:

- `customer_id`
- `purchase_frequency`
- `purchase_value`
- `customer_activity`
- `cluster` (existing K-Means result)
- `hierarchical_cluster`
- `segment_name`

## Implementation files

- Existing feature and orchestration service: `backend/services/segmentation_service.py`
- Existing preserved K-Means model: `backend/models/segmentation/kmeans_model.py`
- New hierarchical model: `backend/models/segmentation/hierarchical_model.py`

Run from the repository root:

```powershell
python -m backend.services.segmentation_service
```

## Limitations

- The labels describe the current sample's three behavioral features and should be reviewed against business context.
- Cluster identifiers are method-generated labels, not permanent customer categories.
- Ward linkage requires a chosen cluster count here; this milestone reuses the K-Means elbow choice rather than introducing a second cluster-selection procedure.
- No forecasting, recommendations, churn, anomaly detection, frontend, or API functionality is added in this milestone.
