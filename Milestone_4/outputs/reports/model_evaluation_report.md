# Comprehensive Machine Learning Model Evaluation Report (Milestone 2)

## 1. Overview
This technical evaluation report details the quantitative validation of machine learning models implemented in Milestone 2 of MarketMind AI:
1. **Unsupervised Customer Segmentation** (K-Means vs. Hierarchical Agglomerative Clustering)
2. **Supervised Sales Forecasting** (Prophet vs. XGBoost vs. Random Forest)

---

## 2. Customer Segmentation Model Evaluation

### 2.1 Silhouette Score Analysis
* **K-Means (k=2):** Silhouette Score = **0.2733**
* **Hierarchical Ward (k=2):** Silhouette Score = **0.3013**

### 2.2 Methodology & Observations
* Features evaluated: Recency (days), Order Frequency, Monetary Spend, Average Order Value (AOV), Total Profit, and Mean Discount Rate.
* Hierarchical Agglomerative Clustering with Ward linkage achieved a slightly higher Silhouette Score (0.3013), but K-Means (0.2733) produced highly interpretable, stable clusters that map cleanly to business operation requirements.

---

## 3. Sales Forecasting Model Evaluation

### 3.1 Quantitative Performance Metrics

| Model | MAE ($) | RMSE ($) | R² Score | MAPE (%) | Ranking |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Prophet** | $11,644.26 | $14,393.83 | **0.6881** | **20.80%** | **1 (Best)** |
| **XGBoost** | $14,471.17 | $18,058.11 | 0.5091 | 21.89% | 2 |
| **Random Forest** | $15,933.62 | $19,699.47 | 0.4158 | 24.28% | 3 |

### 3.2 Technical Analysis & Model Comparison
* **Why Prophet Wins:** Prophet is designed specifically for time series with strong yearly seasonality and holistic trend change points. Its additive decomposition captures annual retail cycles better than non-linear tree splits.
* **XGBoost & Random Forest Limitations:** Tree-based regressors rely on lag features (y_lag1, y_lag12) and cannot extrapolate trend beyond the historical min/max values as effectively in recursive multi-step forecasting horizons.
