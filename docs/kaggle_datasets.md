# Kaggle Datasets Integration Guide — MarketMind AI

MarketMind AI integrates real-world enterprise retail data using `kagglehub` across two core operational pillars:
1. **Sales Transactions & Customer Intelligence**: E-Commerce transactional records spanning customer purchase histories, products, order values, and dates.
2. **Store Inventory & Demand Forecasting**: Multi-store stock monitoring, units ordered, replenishment thresholds, competitor pricing, seasonality, and demand forecasts.

---

## 1. Datasets Overview

| Dataset Identifier | Format & Size | Domain in MarketMind AI | Key Features |
|---|---|---|---|
| **`umerkk12/online-retail-business`**<br>(or `divanshu22/online-retail-dataset`) | CSV (44 MB) / XLSX (22 MB)<br>~541,909 transactions | **Sales Analytics, Forecasting & Customer Intelligence** | `InvoiceNo`, `StockCode`, `Description`, `Quantity`, `InvoiceDate`, `UnitPrice`, `CustomerID`, `Country` |
| **`anirudhchauhan/retail-store-inventory-forecasting-dataset`** | CSV (5.9 MB)<br>73,100 records | **Inventory Control & Demand Replenishment** | `Date`, `Store ID`, `Product ID`, `Category`, `Region`, `Inventory Level`, `Units Sold`, `Units Ordered`, `Demand Forecast`, `Price`, `Discount`, `Weather`, `Seasonality` |

---

## 2. Architecture & Data Mapping

### A. Sales Transactions Mapping (`online-retail-business`)
- `InvoiceNo` -> `order_id` (Numeric integer order identifier)
- `Description` -> `product_name` (Catalog product title)
- `Quantity` -> `quantity` (Units purchased, validated > 0)
- `UnitPrice` -> `unit_price` (Unit price in $, validated > 0)
- `InvoiceDate` -> `order_date` (`YYYY-MM-DD` normalized date)
- `CustomerID` -> `customer_id` (`C<ID>` client identifier)
- Computed: `total_amount = quantity * unit_price`

### B. Store Inventory Mapping (`retail-store-inventory-forecasting-dataset`)
- `Date` -> `date`
- `Store ID` -> `store_id` (Multi-location store code)
- `Product ID` / `Category` -> `category` (Groceries, Toys, Electronics, Furniture, Clothing)
- `Inventory Level` -> `stock_level` (Current on-hand stock)
- `Units Ordered` -> `reorder_point` (Target replenishment threshold)
- Alert condition: `is_low_stock = stock_level < reorder_point`
- Demand signal: `demand_forecast`, `units_sold`, `discount`, `competitor_pricing`

---

## 3. Quick CLI Commands

### Download Datasets
Downloads the latest version directly using `kagglehub`:
```powershell
.\.venv\Scripts\python.exe backend/ingest_kaggle_data.py --action download
```

### Export Cleaned CSVs
Extracts, cleans, standardizes schemas, and exports to `data/processed/`:
```powershell
.\.venv\Scripts\python.exe backend/ingest_kaggle_data.py --action export --limit 5000
```
Generated files:
- `data/processed/kaggle_clean_sales.csv`
- `data/processed/kaggle_clean_inventory.csv`

### Seed SQLite Database with Kaggle Data
Populates SQLite (`db/marketmind.db`) with real products, customers, transactions, invoices, and inventory items:
```powershell
.\.venv\Scripts\python.exe backend/ingest_kaggle_data.py --action seed --limit 500 --wipe
```
Or via `load_data.py`:
```powershell
.\.venv\Scripts\python.exe backend/load_data.py --source kaggle --limit 500 --wipe
```

### Reset to Milestone 1 Test Demo Data (8 records)
Whenever you want to run the strict 8-record regression test suite:
```powershell
.\.venv\Scripts\python.exe backend/load_data.py --source demo
```

### Explore and Profile Datasets
```powershell
# Profile all datasets (Raw demo + Kaggle Clean Sales + Kaggle Clean Inventory)
.\.venv\Scripts\python.exe backend/data_exploration.py --dataset all
```

---

## 4. Python Programmatic Usage

```python
import kagglehub
from backend.kaggle_loader import load_online_retail, load_retail_inventory

# 1. Load clean sales records ready for MarketMind AI
sales_df = load_online_retail(sample_size=1000, as_sales_format=True)
print(sales_df.head())

# 2. Load clean store inventory records
inv_df = load_retail_inventory(sample_size=1000, standardize_columns=True)
print(inv_df.head())
```
