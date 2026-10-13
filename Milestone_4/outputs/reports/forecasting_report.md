# Sales & Revenue Forecasting Report (Milestone 2)

## Executive Summary
This report evaluates future sales and revenue projections for MarketMind AI across a **12-month horizon** using historical monthly data spanning **2014-01 to 2016-12** to **2017-01 to 2017-12**. Three distinct machine learning algorithms were trained and evaluated: **Prophet**, **XGBoost Regressor**, and **Random Forest Regressor**.

## Measured Model Evaluation Summary
* **Evaluation Train Period:** 2014-01 to 2016-12
* **Evaluation Test Period:** 2017-01 to 2017-12
* **Best Performing Model:** **Prophet**

| Model | MAE ($) | RMSE ($) | R² Score | MAPE (%) |
| :--- | :--- | :--- | :--- | :--- |
| **Prophet** | $11,644.26 | $14,393.83 | **0.6881** | **20.80%** |
| **XGBoost** | $14,471.17 | $18,058.11 | 0.5091 | 21.89% |
| **Random Forest** | $15,933.62 | $19,699.47 | 0.4158 | 24.28% |

---

## Business Insights & Revenue Trends
1. **Seasonal Q4 Revenue Peaks:** Monthly sales display strong end-of-year seasonality (November-December spikes), driven by holiday spending and annual business procurement.
2. **Prophet Model Superiority:** Meta Prophet achieved the highest R² (0.6881) and lowest RMSE ($14,393.83) due to its explicit decomposition of additive trend and yearly seasonality.
3. **Inventory & Capital Allocation:** Inventory procurement should be scaled up starting in September/October to capture peak Q4 demand without risking stockouts.
