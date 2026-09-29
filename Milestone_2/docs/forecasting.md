# Milestone 2 — Sales & Revenue Forecasting Documentation

## 1. Overview
Sales & Revenue Forecasting in Milestone 2 projects future monthly sales and revenue trends for MarketMind AI across a 12-month future horizon (2018).

Three distinct machine learning models were developed, back-tested, and evaluated:
1. **Prophet** (Meta Time Series Decomposer)
2. **XGBoost Regressor** (Gradient Boosting Machine)
3. **Random Forest Regressor** (Ensemble Tree Model)

---

## 2. Time-Series Data Preparation

- **Historical Granularity:** Monthly resampled time series spanning Jan 2014 to Dec 2017 (48 historical months).
- **Target Variable ($y$):** Cumulative monthly sales amount ($).
- **Engineered Features:**
  - Lags: `y_lag1`, `y_lag2`, `y_lag3`, `y_lag12`
  - Rolling Averages: `y_roll3`, `y_roll6`
  - Calendar Features: `month`, `quarter`, `year`

---

## 3. Measured Model Evaluation Metrics

Holdout Test Period: Jan 2017 – Dec 2017 (12 months)

| Model | MAE ($) | RMSE ($) | R² Score | MAPE (%) | Ranking |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Prophet** | **$11,644.26** | **$14,393.83** | **0.6881** | **20.80%** | **1 (Best)** |
| **XGBoost** | $14,471.17 | $18,058.11 | 0.5091 | 21.89% | 2 |
| **Random Forest** | $15,933.62 | $19,699.47 | 0.4158 | 24.28% | 3 |

---

## 4. Key Findings
- **Prophet** outperformed tree-based models by capturing additive yearly seasonality and long-term trends effectively.
- Retail sales exhibit strong Q4 seasonal surges (November–December peaks), which Prophet models accurately.

---

## 5. Artifacts & Outputs
- `Milestone_2/outputs/forecasting/prophet_forecast.csv`
- `Milestone_2/outputs/forecasting/xgboost_forecast.csv`
- `Milestone_2/outputs/forecasting/random_forest_forecast.csv`
- `Milestone_2/outputs/forecasting/combined_forecasts.csv`
- `Milestone_2/outputs/forecasting/model_metrics.json`
