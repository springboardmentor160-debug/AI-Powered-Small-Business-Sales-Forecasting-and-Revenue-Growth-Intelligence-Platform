# MarketMind AI: Forecasting Model Comparison

## Milestone 2, Day 7-8

This milestone extends the Day 5-6 Prophet setup with time-series feature engineering, XGBoost, Random Forest, actual chronological evaluation, and selected-model future forecasts. No reporting, recommendations, churn, or anomaly detection is implemented.

## Data and feature engineering

The service reuses the existing processed Sales data and the daily data preparation from the prior milestone:

- Input: `data/processed/sales/cleaned_sales.csv`
- Historical range: **2023-01-01 to 2025-12-31**
- Daily rows: **1,096**

The tree models use the daily `revenue` and `sales_quantity` targets with these features:

- Lag values: 1, 7, 14, and 28 days.
- Rolling means: 7, 14, and 28 days.
- Rolling standard deviations: 7, 14, and 28 days.
- Calendar features: day of week, day of month, month, quarter, day of year, and weekend indicator.

Lag and rolling features use only observations before the target date. Future tree predictions are generated recursively, using earlier predictions as future lag values. No random shuffle is applied.

The prepared feature dataset is saved to:

`data/processed/forecast/feature_engineered_sales.csv`

## Chronological train/validation split

The latest 30 daily observations are held out as validation data:

- Training rows: **1,066**
- Validation rows: **30**
- Validation range: **2025-12-02 to 2025-12-31**

The same chronological validation period is used for Prophet, XGBoost, and Random Forest. Metrics are calculated from actual validation targets.

## Models used

- **Prophet:** Existing implementation from `backend/models/forecasting/prophet_model.py`, with yearly and weekly seasonality.
- **XGBoost Regressor:** Deterministic configuration with `random_state=42`, 250 estimators, depth 4, learning rate 0.05, and one worker.
- **Random Forest Regressor:** Deterministic configuration with `random_state=42`, 250 estimators, depth 12, minimum leaf size 2, and one worker.

## Actual validation comparison

| Metric         | Model         |    MAE |   RMSE | Selected |
| -------------- | ------------- | -----: | -----: | -------- |
| Revenue        | Prophet       | 139.28 | 167.84 | No       |
| Revenue        | XGBoost       | 141.44 | 178.17 | No       |
| Revenue        | Random Forest | 131.74 | 163.80 | Yes      |
| Sales quantity | Prophet       |   5.90 |   7.66 | Yes      |
| Sales quantity | XGBoost       |   6.54 |   8.28 | No       |
| Sales quantity | Random Forest |   6.13 |   7.90 | No       |

The selected model for each target is the model with the lowest RMSE, with MAE used as the tie-breaker:

- **Revenue:** Random Forest
- **Sales quantity:** Prophet

## Actual future forecast output

The selected forecast covers **2026-01-01 to 2026-01-30**:

| Date       | Metric         | Selected model | Forecast |
| ---------- | -------------- | -------------- | -------: |
| 2026-01-01 | revenue        | Random Forest  |   425.11 |
| 2026-01-01 | sales_quantity | Prophet        |    25.95 |
| 2026-01-02 | revenue        | Random Forest  |   398.33 |
| 2026-01-02 | sales_quantity | Prophet        |    26.08 |
| 2026-01-03 | revenue        | Random Forest  |   464.47 |
| 2026-01-03 | sales_quantity | Prophet        |    29.33 |

## Outputs

- `data/processed/forecast/feature_engineered_sales.csv`
- `data/processed/forecast/model_comparison.csv`
- `data/processed/forecast/model_validation_predictions.csv`
- `data/processed/forecast/model_forecasts.csv` contains future predictions from all three models.
- `data/processed/forecast/sales_forecast.csv` contains the selected model forecast per target.

## Run command

From the repository root:

```powershell
.venv\Scripts\python.exe -m backend.services.forecasting_service
```

The service prints the chronological split, every model's MAE/RMSE result, selected models, forecast preview, and output paths.

## Limitations

- Evaluation uses one 30-day chronological holdout.
- Tree-model validation uses lag and rolling features derived from prior observed daily values; future tree forecasts use recursive predictions.
- The current comparison covers aggregate revenue and sales quantity only.
- Hyperparameter tuning and broader time-series backtesting are outside this milestone.
