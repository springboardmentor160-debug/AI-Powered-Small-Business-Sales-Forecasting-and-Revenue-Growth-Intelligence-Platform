# Milestone 2 — System Architecture & Execution Guide

## Overview
**MarketMind AI — Milestone 2** is an independent, modular machine learning platform providing:
1. **Customer Segmentation:** K-Means & Hierarchical Agglomerative Clustering
2. **Sales & Revenue Forecasting:** Prophet, XGBoost, and Random Forest Regressors
3. **Model Evaluation & Insights:** Empirical performance validation and business reporting
4. **Interactive Dashboard & API:** FastAPI backend and modern glassmorphic web dashboard UI

> **SAFETY NOTICE:** Milestone 1 (`d:/AI Powered Small Forecasting System/Milestone_1`) is completely read-only and untouched. Milestone 2 operates on copied data stored in `Milestone_2/data/source/`.

---

## 1. Project Directory Structure

```
Milestone_2/
├── data/
│   ├── source/               # Read-only copies of Milestone 1 data
│   └── processed/            # Engineered features & processed time series
├── ml/
│   ├── segmentation/         # Feature engineering, K-Means, Hierarchical, Evaluation
│   └── forecasting/          # Data preparation, Prophet, XGBoost, RF, Evaluation
├── outputs/
│   ├── segmentation/         # Customer segments CSV, Cluster summary, Metrics JSON
│   ├── forecasting/          # Prophet, XGBoost, RF forecasts & Model metrics
│   └── reports/              # Markdown business reports
├── backend/
│   ├── main.py               # FastAPI entrypoint
│   ├── routes.py             # API endpoints (/api/overview, /api/forecasting, etc.)
│   └── models.py             # Pydantic schemas
├── frontend/
│   ├── index.html            # Dashboard UI
│   ├── index.css             # Glassmorphic CSS design system
│   └── app.js                # Interactive Chart.js & API integration
├── notebooks/
│   ├── 01_customer_segmentation.ipynb
│   └── 02_sales_forecasting.ipynb
├── tests/
│   ├── test_segmentation.py  # Segmentation pipeline tests
│   ├── test_forecasting.py   # Forecasting pipeline tests
│   └── test_api.py           # Backend API tests
└── docs/
    ├── MILESTONE_1_REFERENCE.md
    ├── segmentation.md
    ├── forecasting.md
    └── MILESTONE_2.md
```

---

## 2. How to Run Milestone 2

### Step 1: Run ML Pipelines (Generate Outputs)
From the root directory (`d:\AI Powered Small Forecasting System`):

```bash
# 1. Run Customer Segmentation Pipeline
python -m Milestone_2.ml.segmentation.evaluation

# 2. Run Sales & Revenue Forecasting Pipeline
python -m Milestone_2.ml.forecasting.evaluation
```

### Step 2: Run Test Suite
```bash
python -m unittest discover -s Milestone_2/tests -p "test_*.py"
```

### Step 3: Launch FastAPI Backend & Dashboard UI
```bash
python -m uvicorn Milestone_2.backend.main:app --host 127.0.0.1 --port 8000 --reload
```
Open your browser at:
`http://127.0.0.1:8000`

---

## 3. Key Measured Results

* **Customer Segmentation:**
  - Optimal Clusters: $k = 2$
  - Hierarchical Silhouette Score: **0.3013**
  - K-Means Silhouette Score: **0.2733**
  - **High-Value Champions:** 528 customers (66.58%), generating **89.60%** of total revenue.
  - **Low-Activity / At-Risk:** 265 customers (33.42%), generating **10.40%** of total revenue.

* **Sales Forecasting Model Comparison:**
  - **Prophet (Winner):** MAE = $11,644.26, RMSE = **$14,393.83**, $R^2$ = **0.6881**
  - **XGBoost:** MAE = $14,471.17, RMSE = $18,058.11, $R^2$ = 0.5091
  - **Random Forest:** MAE = $15,933.62, RMSE = $19,699.47, $R^2$ = 0.4158
