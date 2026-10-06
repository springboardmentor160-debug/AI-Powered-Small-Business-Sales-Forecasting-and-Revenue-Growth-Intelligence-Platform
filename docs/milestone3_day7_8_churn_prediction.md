# MarketMind AI: Churn Model Comparison and Retention Risk

## Milestone 3, Day 7-8

This milestone compares Logistic Regression, Random Forest, and XGBoost using the same M3 Day 5-6 customer churn features and the same stratified customer-level split. It generates probability-based retention risk and connects each result to the existing Milestone 2 customer segment.

## Why accuracy is insufficient

The actual target is imbalanced: 8 churned customers versus 292 non-churned customers. A model could achieve high accuracy by favoring the majority class while missing churned customers. Recall is especially important because missing a genuinely at-risk customer can be more costly than creating a false alarm. Model selection therefore prioritizes F1-score first and Recall second, rather than accuracy alone.

## Shared data and split

The existing M3 Day 5-6 features are reused:

- `recency_days`
- `purchase_frequency`
- `average_order_value`
- `customer_activity`

The churn definition is unchanged: `recency_days > 90`, using the actual reference date **2025-12-31**. All three models use the same deterministic stratified 75/25 customer-level split with `random_state=42`.

## Model comparison

| Model               | Precision | Recall | F1-score | Selected |
| ------------------- | --------: | -----: | -------: | -------- |
| Random Forest       |    1.0000 | 1.0000 |   1.0000 | Yes      |
| XGBoost             |    1.0000 | 1.0000 |   1.0000 | No       |
| Logistic Regression |    0.6667 | 1.0000 |   0.8000 | No       |

Random Forest was selected because it tied XGBoost on F1 and Recall and won the deterministic model-name tie-break. Both tree models achieved perfect validation metrics on this small holdout; this should not be interpreted as proof of production-level generalization.

## Probability generation and risk thresholds

The selected model generates churn probabilities with `model.predict_proba()`. Each customer is assigned exactly according to the official thresholds:

- `churn_probability >= 0.70`: **High Risk**
- `0.40 <= churn_probability < 0.70`: **Medium Risk**
- `churn_probability < 0.40`: **Low Risk**

Actual risk counts:

| Retention risk | Customers |
| -------------- | --------: |
| High Risk      |         8 |
| Medium Risk    |         0 |
| Low Risk       |       292 |

## Connection to Milestone 2 segmentation

Final churn predictions are joined to `data/processed/segments/customer_segments.csv` using `customer_id`. Existing segment names are preserved exactly:

| Segment                | High Risk | Medium Risk | Low Risk | Total |
| ---------------------- | --------: | ----------: | -------: | ----: |
| High Value Customers   |         0 |           0 |       51 |    51 |
| Low Activity Customers |         4 |           0 |       48 |    52 |
| Regular Customers      |         4 |           0 |      193 |   197 |

## Generated outputs

- `data/processed/churn/churn_model_comparison.csv`
- `data/processed/churn/churn_predictions_final.csv`
- `data/processed/churn/churn_segment_risk_summary.csv`

The final customer-level output contains the churn features, actual `churned` label, `predicted_churn`, `churn_probability`, `retention_risk`, existing `segment_name`, and selected model.

## Limitations

- Only one stratified holdout is used; no cross-validation or model comparison across multiple time periods is included yet.
- The target is derived from inactivity in the same historical dataset, not from a separately observed future cancellation outcome.
- The class distribution is highly imbalanced at 8 churned versus 292 non-churned customers.
- Perfect tree-model validation scores on this small holdout may not generalize to future data.
- Retention-risk categories are initial threshold outputs, not a retention action system.

## Run command

From the repository root:

```powershell
.venv\Scripts\python.exe -m backend.services.churn_comparison_service
```
