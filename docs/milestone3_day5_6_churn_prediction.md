# MarketMind AI: Customer Churn Prediction Baseline

## Milestone 3, Day 5-6

This milestone creates the initial customer churn dataset and Logistic Regression baseline using actual processed Sales and Customer data. It does not implement model comparison, retention-risk categories, anomaly detection, or other later modules.

## Churn definition and reference date

A customer is labeled **churned** when they have made no purchase for more than 90 days.

The reference date is the latest transaction date in the actual processed Sales dataset:

- Reference date: **2025-12-31**
- Churn rule: `recency_days > 90`

The raw and processed source datasets are read only and are not modified.

## Customer-level features

The feature dataset is aggregated by `customer_id`:

- **`recency_days`:** Days between the customer's most recent purchase and the reference date.
- **`purchase_frequency`:** Number of distinct sales transactions for the customer.
- **`average_order_value`:** Mean `total_amount` across the customer's transactions.
- **`customer_activity`:** Number of distinct calendar dates on which the customer purchased.

Customer IDs from the processed Customer dataset are retained. If a future customer has no Sales history, the service gives that customer zero frequency, average order value, and activity, and assigns an observation-window recency so the 90-day rule remains explicit.

## Actual class distribution

The current generated dataset contains:

| Class       | Customers |
| ----------- | --------: |
| Churned     |         8 |
| Non-churned |       292 |

This is an imbalanced target, but both classes are present. No customers were fabricated or relabeled to balance the data. Logistic Regression uses `class_weight="balanced"` to account for the minority class.

## Logistic Regression baseline

The model is implemented in `backend/models/churn/logistic_regression_model.py` and orchestrated by `backend/services/churn_service.py`.

Preprocessing and training:

- Features are standardized with `StandardScaler` inside a pipeline.
- Logistic Regression uses `max_iter=1000`, `class_weight="balanced"`, and `random_state=42`.
- A deterministic stratified 75/25 customer-level split is used because both classes have enough examples.
- This milestone does not compare Logistic Regression with Random Forest or XGBoost.

## Actual validation result

| Metric    | Result |
| --------- | -----: |
| Accuracy  | 0.9867 |
| Precision | 0.6667 |
| Recall    | 1.0000 |
| F1        | 0.8000 |
| ROC-AUC   | 1.0000 |

The generated predictions include a churn probability for every processed customer. These are baseline probabilities from the fitted Logistic Regression model, not retention-risk categories.

## Generated outputs

- `data/processed/churn/customer_churn_features.csv`
- `data/processed/churn/churn_predictions.csv`
- `data/processed/churn/churn_model_metrics.csv`

`customer_churn_features.csv` contains the customer features and actual `churned` label. `churn_predictions.csv` contains actual labels, predicted labels, churn probabilities, and model name. `churn_model_metrics.csv` contains the actual validation result.

## Limitations

- The target is derived from inactivity in the same generated historical dataset, not from a separately observed future cancellation outcome.
- Only one stratified holdout is used; no Day 7-8 model comparison or broader backtesting is included.
- The 8-to-292 class distribution is highly imbalanced, so precision and recall should be interpreted with the class counts in mind.
- The current features describe purchase recency, frequency, value, and observed activity only.

## Run command

From the repository root:

```powershell
.venv\Scripts\python.exe -m backend.services.churn_service
```
