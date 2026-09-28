# MarketMind AI: Forecasting Setup

## Milestone 2, Day 5-6

This milestone prepares historical sales time series and generates the first Prophet forecast from the existing cleaned Sales dataset. XGBoost, Random Forest, model comparison, recommendations, churn, and anomaly detection are not included.

## Data preparation

Input:

- `data/processed/sales/cleaned_sales.csv`

The service reads the processed file without modifying it, parses `date` with pandas, and converts `quantity` and `total_amount` to numeric values. Invalid rows that cannot provide these required forecasting values are excluded from the in-memory preparation only.

## Time-series aggregation

The overall daily dataset is grouped by `date` and contains:

- `sales_quantity`: total quantity sold on the date.
- `revenue`: total `total_amount` on the date.
- `transaction_count`: unique transactions on the date.
- `day_of_week`: pandas day-of-week number.
- `month`: calendar month.
- `is_weekend`: weekend indicator.

Missing calendar dates between the first and last observed dates are inserted with zero totals so the daily series is continuous. A product-level daily dataset is also prepared with `date`, `product_id`, `product_name`, `sales_quantity`, and `revenue`.

Actual preparation results:

- Processed sales rows: **12,000**
- Daily overall rows: **1,096**
- Product-day rows: **9,611**
- Historical range: **2023-01-01 to 2025-12-31**

## Chronological validation split

The latest 30 historical days are held out as validation data. No random shuffle is used:

- Training rows: **1,066**
- Validation rows: **30**
- Validation range: **2025-12-02 to 2025-12-31**

Prophet is first fitted on the training prefix and evaluated on this chronological holdout. It is then refitted on all available historical daily data before generating the future forecast.

## Prophet configuration

The first model is the reusable `ProphetForecaster` in `backend/models/forecasting/prophet_model.py`.

- Yearly seasonality: enabled
- Weekly seasonality: enabled
- Daily seasonality: disabled
- Seasonality mode: additive
- Changepoint prior scale: `0.05`
- Uncertainty samples: `0` for a deterministic point forecast
- Forecast horizon: **30 days**

## Actual validation results

| Metric         | Mean absolute error |
| -------------- | ------------------: |
| Revenue        |              139.28 |
| Sales quantity |                5.90 |

## Actual future forecast preview

The generated forecast begins as follows:

| Date       | Metric         | Forecast |
| ---------- | -------------- | -------: |
| 2026-01-01 | revenue        |   436.95 |
| 2026-01-01 | sales_quantity |    25.95 |
| 2026-01-02 | revenue        |   433.90 |
| 2026-01-02 | sales_quantity |    26.08 |
| 2026-01-03 | revenue        |   491.33 |
| 2026-01-03 | sales_quantity |    29.33 |

The actual 30-day future forecast covers **2026-01-01 to 2026-01-30**.

## Outputs

The service writes:

- `data/processed/forecast/daily_sales.csv`
- `data/processed/forecast/daily_product_sales.csv`
- `data/processed/forecast/sales_forecast.csv`

The combined forecast file contains `date`, `metric`, and `forecast` rows for revenue and sales quantity.

## Implementation

- Prophet model wrapper: `backend/models/forecasting/prophet_model.py`
- Data preparation and forecasting service: `backend/services/forecasting_service.py`

Run from the repository root:

```powershell
.venv\Scripts\python.exe -m backend.services.forecasting_service
```

## Limitations

- This is an initial Prophet setup using aggregate daily data, not a final production forecast.
- The validation window is one 30-day chronological holdout and should be expanded in later model-evaluation work.
- Product-level data is prepared for future use, but separate product forecasts are not generated in this milestone.
- No uncertainty interval, model comparison, or advanced feature engineering is included yet.
