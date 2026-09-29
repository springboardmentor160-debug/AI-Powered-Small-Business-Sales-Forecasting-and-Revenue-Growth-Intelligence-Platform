# Milestone 1 Data & Architecture Reference Document

## Overview
This document serves as the official reference guide for data sources copied from Milestone 1 for use in **Milestone 2 (MarketMind AI)**.

> **CRITICAL COMPLIANCE NOTICE:**
> Milestone 1 (`d:/AI Powered Small Forecasting System/Milestone_1`) is strictly **READ-ONLY** and frozen. 
> All files inside `Milestone_1` remain untouched.
> Source datasets have been copied to `Milestone_2/data/source/` for independent preprocessing and model training.

---

## 1. Datasets Used in Milestone 2

The following datasets copied from `Milestone_1/data/processed/` and `Milestone_1/data/raw/` are utilized in Milestone 2:

### 1.1 `cleaned_superstore.csv`
* **Original Location:** `Milestone_1/data/processed/cleaned_superstore.csv`
* **Milestone 2 Location:** `Milestone_2/data/source/cleaned_superstore.csv`
* **Volume:** 9,994 rows, 21 columns
* **Required Columns:** 
  - `order_id`, `order_date`, `ship_date`, `ship_mode`
  - `customer_id`, `customer_name`, `segment`, `country`, `city`, `state`, `postal_code`, `region`
  - `product_id`, `category`, `sub_category`, `product_name`
  - `sales`, `quantity`, `discount`, `profit`
* **Why Required:** Provides full granular transactional data including customer identifiers, product hierarchy, exact dates, sales monetary values, order quantities, discounts, and profits.
* **How Used in Milestone 2:**
  - **Customer Segmentation:** To calculate Recency (days since last purchase), Frequency (total orders count), Monetary Value (total spend), Average Order Value (AOV), Profit Contribution, Total Quantity, and Discount Sensitivity per `customer_id`.
  - **Sales & Revenue Forecasting:** To aggregate daily, weekly, and monthly sales and profit revenue time-series data from Jan 2014 to Dec 2017 for Prophet, XGBoost, and Random Forest models.

### 1.2 `sales.csv`
* **Original Location:** `Milestone_1/data/processed/sales.csv`
* **Milestone 2 Location:** `Milestone_2/data/source/sales.csv`
* **Volume:** 9,994 rows, 6 columns
* **Required Columns:** `id`, `product_id`, `customer_id`, `quantity`, `sales_amount`, `sale_date`
* **Why Required:** Normalized transaction table linking product IDs, customer IDs, sale dates, quantities, and sales amounts.
* **How Used in Milestone 2:** Used for fast normalized relational joins and time-series aggregation validation.

### 1.3 `customers.csv` / `dim_customers.csv`
* **Original Location:** `Milestone_1/data/processed/customers.csv`
* **Milestone 2 Location:** `Milestone_2/data/source/customers.csv`
* **Volume:** 793 rows, 8 columns
* **Required Columns:** `customer_id`, `name`, `segment`, `country`, `city`, `state`, `postal_code`, `region`
* **Why Required:** Master list of 793 unique customers and their baseline demographic segment (Consumer, Corporate, Home Office) and geographic region.
* **How Used in Milestone 2:** Used as the ground-truth customer list to map calculated RFM feature vectors and attach ML-derived clusters (K-Means & Hierarchical) back to customer profile metadata.

### 1.4 `products.csv` / `dim_products.csv`
* **Original Location:** `Milestone_1/data/processed/products.csv`
* **Milestone 2 Location:** `Milestone_2/data/source/products.csv`
* **Volume:** 1,862 rows, 4 columns
* **Required Columns:** `product_id`, `name`, `category`, `unit_price` / `sub_category`
* **Why Required:** Product dimension table containing product names, categories, and pricing.
* **How Used in Milestone 2:** Product-level trend analysis and category-wise sales forecasting breakdowns.

---

## 2. Lineage & Data Safety Protocol

1. **Isolation:** Milestone 2 imports data exclusively from `Milestone_2/data/source/`.
2. **Immutable Source:** Original CSV files in `Milestone_1/` are never written to, overwritten, or moved.
3. **Derived Artifacts:** All Milestone 2 engineered features, trained models, predictions, forecasts, metrics, and visualization outputs are strictly written to:
   - `Milestone_2/data/processed/`
   - `Milestone_2/outputs/segmentation/`
   - `Milestone_2/outputs/forecasting/`
   - `Milestone_2/outputs/reports/`

---

## 3. Milestone 1 Status Confirmation

- [x] `Milestone_1` files inspected and verified.
- [x] Read-only source copies created in `Milestone_2/data/source/`.
- [x] `Milestone_1` directory completely untouched and frozen.
