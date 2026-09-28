# MarketMind AI: Customer Segmentation Setup

## Milestone 2, Day 1-2

This milestone prepares customer-level behavioral features from the existing processed Sales and Customer datasets and applies the initial K-Means segmentation. It does not implement forecasting, recommendations, churn, anomaly detection, or new application endpoints.

## Input and output

Inputs:

- `data/processed/sales/cleaned_sales.csv`
- `data/processed/customers/cleaned_customers.csv`

Output:

- `data/processed/segments/customer_segments.csv`

The raw datasets under `data/raw/` are not modified.

## Features used

Features are aggregated by `customer_id`:

- **`purchase_frequency`:** Number of sales transaction records associated with the customer.
- **`purchase_value`:** Sum of the customer's `total_amount` values across sales transactions.
- **`customer_activity`:** Number of distinct calendar dates on which the customer made a purchase.

Customers are loaded from the Customer dataset first and left-joined with the aggregated Sales features. A customer with no transactions receives `0` for all three behavioral features and remains in the segmentation output.

## Preprocessing

1. Load the processed Sales and Customer CSV files.
2. Parse the Sales `date` field with pandas for distinct activity-day counts.
3. Convert `total_amount` to numeric values and use zero for unavailable aggregation values.
4. Aggregate behavioral features by `customer_id`.
5. Fill missing feature values after the customer left join with zero.
6. Apply `log1p` to reduce the effect of highly skewed frequency and value ranges.
7. Standardize the transformed features with `StandardScaler` before clustering.

## K-Means approach

The implementation uses scikit-learn `KMeans` with `random_state=42` and `n_init=10` for reproducible results. Candidate cluster counts from 2 through 6 are compared using inertia. The initial elbow selection chooses the candidate with the maximum normalized distance from the line connecting the first and last inertia values.

The actual elbow comparison was:

| Clusters (`k`) |  Inertia |
| -------------: | -------: |
|              2 | 413.9496 |
|              3 | 247.7022 |
|              4 | 201.2602 |
|              5 | 167.6316 |
|              6 | 141.2398 |

**Chosen number of clusters: 3**

## Actual result

The run processed 300 customers and produced the following cluster counts:

| Cluster | Customers |
| ------: | --------: |
|       0 |       110 |
|       1 |       138 |
|       2 |        52 |

The output contains `customer_id`, `purchase_frequency`, `purchase_value`, `customer_activity`, and `cluster`.

## Implementation

- Feature and output orchestration: `backend/services/segmentation_service.py`
- K-Means and elbow selection: `backend/models/segmentation/kmeans_model.py`
- Run command from the repository root:

```powershell
python -m backend.services.segmentation_service
```

## Limitations

- The current result is based on the available sample data and only three behavioral features.
- The elbow heuristic provides an initial `k`; it is not a substitute for business review or deeper cluster validation.
- Cluster numbers are identifiers, not business labels or ranked customer-value categories.
- The segmentation output is saved for later use but is not yet exposed through an API, dashboard, or downstream recommendation/churn workflow.
