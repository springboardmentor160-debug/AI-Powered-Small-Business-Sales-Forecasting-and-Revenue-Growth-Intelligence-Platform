## MarketMind AI — Project Objectives & Data Flow

## 1. Project Overview

MarketMind AI is a small business sales intelligence platform designed to track performance metrics, identify customer segments, and surface insights on profitable vs. loss-making products.

## 2. Core Objectives

* **Sales & Margin Tracking:** Monitor total sales, quantity sold, profit margins, and discount impact across regions.
* **Customer Segmentation:** Analyze behavior across Consumer, Corporate, and Home Office segments.
* **Product Insights:** Track category and sub-category sales performance to detect loss-making items.
* **Role-Based Views:** Prepare business data tailored for Business Owners, Store Managers, Sales Executives, and Admins.

## 3. Dataset Summary

* **File:** `Sample - Superstore.csv` (located in `data/raw/`)
* **Volume:** 9,994 records, 21 columns, zero missing values.
* **Dimensions:** Order Date, Ship Mode, Customer ID, Segment, Region, Category, Sub-Category, Product Name.
* **Metrics:** Sales, Quantity, Discount, Profit.

## 4. System Data Flow

1. **Raw Ingestion:** Ingest raw CSV data from `data/raw/`.
2. **Preprocessing (Day 5–6):** Standardize dates, clean schema, and prepare structured tables.
3. **API Layer (Day 7–8):** FastAPI backend handles analytical logic and KPI endpoints.
4. **Dashboard Layer:** Frontend UI displays role-filtered sales charts, summaries, and metrics.
