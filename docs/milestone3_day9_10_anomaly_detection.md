# MarketMind AI: Sales Anomaly Detection

## Milestone 3, Day 9-10

This milestone adds statistical and machine-learning anomaly detection for actual processed Sales transactions. It does not add frontend panels, anomaly APIs, or Milestone 4 functionality.

## Objective and data

The pipeline reads `data/processed/sales/cleaned_sales.csv` and does not modify raw or processed source data. The actual Sales schema was inspected before implementation.

The anomaly features are exactly the existing numeric fields:

- `quantity`
- `unit_price`
- `total_amount`

The generated dataset contains **12,000** transactions. No artificial anomalies were injected.

## Z-score methodology

For each anomaly feature, the service calculates a population-standard-deviation Z-score across the actual transaction data. A transaction is flagged by the statistical detector when any selected feature has:

`|z| > 3`

The output keeps the original transaction context and includes the largest absolute Z-score for the flagged row. Alert severity is based on the observed magnitude:

- `3 <= |z| < 4`: Medium
- `4 <= |z| < 5`: High
- `|z| >= 5`: Critical

## Isolation Forest methodology

Isolation Forest runs on the same three numeric features after standardization with `StandardScaler`. It uses:

- `contamination = 0.01`
- `random_state = 42`
- `n_estimators = 200`
- `n_jobs = 1`

The 1% contamination value is a conservative initial alert budget for 12,000 transactions. It limits the expected detector output to approximately 120 records rather than producing an excessive number of alerts. Isolation Forest anomaly scores are retained in the anomaly output and alert records.

## Actual comparison

| Result                       |  Count |
| ---------------------------- | -----: |
| Transactions processed       | 12,000 |
| Z-score anomalies            |    512 |
| Isolation Forest anomalies   |    120 |
| Flagged by both methods      |    120 |
| Total method-specific alerts |    632 |

The 120 Isolation Forest flags are also present in the Z-score set for this generated dataset. The additional 392 Z-score flags are statistical outliers that the Isolation Forest did not select under the 1% contamination budget.

## Actionable alerts

Each alert includes, where available:

- `transaction_id`
- `date`
- `store_id`
- `product_id`
- `product_name`
- `alert_type`
- `message`
- `severity`
- `detection_method`
- `relevant_feature`
- `relevant_value`
- `anomaly_score`

The generated alert severity counts are:

| Severity | Alerts |
| -------- | -----: |
| Medium   |    374 |
| High     |    120 |
| Critical |    138 |

These are detection alerts for business review, not proof of fraud, data error, or operational failure. A user should inspect the transaction context before acting.

## Generated outputs

- `data/processed/anomalies/z_score_anomalies.csv`
- `data/processed/anomalies/isolation_forest_anomalies.csv`
- `data/processed/anomalies/anomaly_comparison.csv`
- `data/processed/anomalies/anomaly_alerts.csv`

Implementation files:

- `backend/models/anomaly/anomaly_detection.py`
- `backend/services/anomaly_service.py`

## Limitations

- The current data is synthetic and contains no known injected anomalies or verified incident labels.
- Z-score detection assumes that unusually distant numeric values are useful review candidates; skewed business distributions can produce legitimate high values.
- Isolation Forest contamination is an initial conservative setting, not a learned business incident rate.
- No frontend, API, alert workflow, or later anomaly-analysis module is implemented in this milestone.

## Run command

From the repository root:

```powershell
.venv\Scripts\python.exe -m backend.services.anomaly_service
```
