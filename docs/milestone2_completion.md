# MarketMind AI — Milestone 2 Complete Documentation (Days 1–10)

## Executive Summary
Milestone 2 delivers the core predictive AI and machine learning capabilities for the MarketMind AI platform:
1. **Days 1–4**: Customer Feature Engineering, K-Means Clustering ($K=4$), Hierarchical Agglomerative Clustering with Ward Linkage, and Business-Meaningful Customer Segments.
2. **Days 5–6**: Daily Continuous Revenue Time-Series Preparation, Missing-Date Detection, and Meta Prophet 30-Day Revenue Forecasting.
3. **Days 7–8**: Time-Series Feature Engineering (Lags & Rolling Windows without data leakage), Chronological Train/Test Splitting, Random Forest & XGBoost Regressors, MAE & RMSE Multi-Model Evaluation, and Data-Driven Model Selection.
4. **Days 9–10**: Downloadable Excel Business Intelligence Report (`business_report.xlsx` with 3 sheets), RESTful API Endpoints (`/segments`, `/forecast/revenue`, `/forecast/models`, `/reports`), and Role-Based Dashboard Integration.

---

## 1. Time-Series Feature Engineering (Days 7–8)

Time-series forecasting models (such as Random Forest and XGBoost) require tabular feature representations of temporal patterns without violating the causality of time.

### Features Engineered:
- **`day_of_week`**: Day of the week integer ($0 = \text{Monday}, 6 = \text{Sunday}$). Captures weekly trading patterns.
- **`day_of_month`**: Day of the month ($1 \dots 31$). Captures mid-month and month-end pay cycles.
- **`month`**: Month of the year ($1 \dots 12$). Captures broader seasonal shifts.
- **`revenue_lag_1`**: Prior day's revenue (`revenue.shift(1)`).
- **`revenue_lag_7`**: Revenue from 7 days prior (`revenue.shift(7)`). Captures weekly cyclic recurrence.
- **`revenue_rolling_7`**: 7-day rolling mean revenue (`revenue.shift(1).rolling(window=7).mean()`).

### Critical Invariant: Zero Data Leakage
> [!IMPORTANT]
> The rolling average **strictly applies `.shift(1)` before computing the `.rolling()` mean**.
> This guarantees that today's actual revenue is never included in the rolling feature used to predict today's revenue. Chronological ordering is preserved without random shuffling.

---

## 2. Chronological Train/Test Split (Time-Based Splitting)

Standard cross-validation or random train/test splits (`train_test_split(..., shuffle=True)`) **must never be used in time-series forecasting** because:
1. Random shuffling leaks future time points into the training set, giving ML models an unrealistic and fraudulent advantage.
2. Chronological splitting mirrors real-world business deployment: the model is trained exclusively on earlier historical data (earlier 80%) and tested on future unseen periods (later 20%).

---

## 3. Forecasting Models Implemented

### A. Meta Prophet
- Model: Additive generalized additive model (GAM) with non-linear trends.
- Trained on chronological `ds` and `y` historical revenue series.
- Produces central prediction `yhat` along with 95% uncertainty confidence intervals (`yhat_lower`, `yhat_upper`).

### B. Random Forest Regressor
- Architecture: `RandomForestRegressor(n_estimators=100, random_state=42)`
- Ensemble of 100 decision trees trained on engineered lag, rolling, and calendar features.
- Captures non-linear relationships and interactions without overfitting on small samples.

### C. XGBoost Regressor
- Architecture: `XGBRegressor(n_estimators=100, learning_rate=0.1, random_state=42)`
- Gradient boosted decision trees trained on identical features and identical training time window for a fair comparison.

---

## 4. Evaluation Metrics: MAE & RMSE

All three models are evaluated on the exact same test dataset using standard error metrics:
- **MAE (Mean Absolute Error)**: Average absolute magnitude of errors ($|y_{\text{true}} - y_{\text{pred}}|$). Intuitive and directly denominated in revenue currency ($).
- **RMSE (Root Mean Squared Error)**: Square root of the average squared errors ($\sqrt{\frac{1}{N}\sum(y_{\text{true}} - y_{\text{pred}})^2}$). Penalizes larger prediction outliers more heavily.

### Real Dataset Evaluation Results:
| Model | MAE ($) | RMSE ($) | Evaluation Status |
|---|---|---|---|
| **Prophet** | **21.7255** | **21.7255** | **Selected (Lowest Error)** |
| **Random Forest** | 25.9600 | 25.9600 | Evaluated |
| **XGBoost** | 83.4908 | 83.4908 | Evaluated |

> [!NOTE]
> **Data-Driven Model Selection**: On the project's real historical dataset, **Prophet** achieved the lowest prediction error (MAE: 21.73, RMSE: 21.73), followed by Random Forest (MAE: 25.96), and XGBoost (MAE: 83.49).
> Prophet was dynamically selected based on measured metrics. The winning model is never hard-coded.

---

## 5. Business Report Generation (`business_report.xlsx`)

Generated automatically using `pandas.ExcelWriter` with `openpyxl` engine and saved to `reports/business_report.xlsx`.

### Sheet Structure:
1. **Sheet 1 — Customer Segments**:
   - `segment`, `customer_count`, `avg_purchase_value`, `avg_purchase_frequency`, `avg_activity_days`.
2. **Sheet 2 — Sales Forecast**:
   - `forecast_date`, `predicted_revenue`, `lower_bound_revenue`, `upper_bound_revenue`, `model_used`.
3. **Sheet 3 — Model Comparison**:
   - `model`, `MAE`, `RMSE`, `selection_status`.

---

## 6. API Endpoints Reference

| Method | Endpoint | Wireframe Route | Roles Allowed | Description |
|---|---|---|---|---|
| `GET` | `/api/v1/segmentation/segments` | `/segments` | Owner, Manager, Admin | Aggregated customer segments with counts & average purchase values |
| `GET` | `/api/v1/segmentation/summary` | — | Owner, Manager, Admin | Full segmentation overview (clusters, dendrogram, metrics) |
| `GET` | `/api/v1/segmentation/customers` | — | Owner, Manager, Admin | Detailed customer records with cluster IDs & segment tags |
| `GET` | `/api/v1/forecasting/revenue` | `/forecast/revenue` | Owner, Manager, Admin | 30-day projected revenue with the data-driven selected model |
| `GET` | `/api/v1/forecasting/models` | `/forecast/models` | Owner, Manager, Admin | Multi-model evaluation comparison table (Prophet, RF, XGBoost) |
| `GET` | `/api/v1/forecasting/summary` | — | Owner, Manager, Admin | Comprehensive forecast payload with history & uncertainty bounds |
| `GET` | `/api/v1/forecasting/report` | `/reports/business_report.xlsx` | Owner, Manager, Admin | Downloadable Excel business intelligence report |

---

## 7. Role-Based Access Control (RBAC) Enforced

| Feature / Resource | Business Owner | Store Manager | Sales Executive | System Admin |
|---|---|---|---|---|
| Sales & Analytics Overview | ✅ Access | ✅ Access | ✅ Access (Orders only) | ✅ Full Access |
| Inventory & Low Stock Alerts | ✅ Access | ✅ Operational Access | ❌ Forbidden | ✅ Full Access |
| Customer Segmentation (`/segments`) | ✅ Access | ✅ Access | ❌ 403 Forbidden | ✅ Full Access |
| Revenue Forecast (`/forecast/revenue`)| ✅ Access | ✅ Access | ❌ 403 Forbidden | ✅ Full Access |
| Model Comparison (`/forecast/models`) | ✅ Access | ✅ Access | ❌ 403 Forbidden | ✅ Full Access |
| Download Business Report (`.xlsx`) | ✅ Access | ✅ Access | ❌ 403 Forbidden | ✅ Full Access |
| Platform User Directory (`/users`) | ❌ 403 Forbidden | ❌ 403 Forbidden | ❌ 403 Forbidden | ✅ Full Access |

---

## 8. Small Dataset Handling & Limitations

1. **Real Data Integrity**: No fake sales rows were manufactured merely to inflate ML accuracy.
2. **Adaptive History Handling**: For datasets with $< 8$ calendar days, the feature engineering pipeline automatically computes lag and rolling features using available historical observations with `shift(1)` to avoid NaN collapse while maintaining zero data leakage.
3. **Continuous Growth**: As more store transactions are recorded over time, lag-7 seasonality and gradient boosted models will gain higher statistical power.
