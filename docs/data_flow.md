# MarketMind AI: Data Flow

## Planned platform flow

The following flow describes how MarketMind AI is expected to move data from raw business inputs to business insights. It is a planned architecture for future milestones; Milestone 1, Day 1-2 implements only the raw sample data, exploration, and documentation stages.

```text
Raw Sales Data
Raw Inventory Data
Raw Customer Data
  |
  v
Data Exploration
  |
  v
Data Cleaning
  |
  v
Processed Data
  |
  v
Database
  |
  v
FastAPI Backend
  |
  v
Business Analytics / AI Modules
  |
  v
Dashboard / Reports
```

## Stage descriptions

### 1. Raw Sales Data

Sales transaction records are received in `data/raw/sales/sales.csv`. They contain transaction dates, products, quantities, prices, revenue, stores, customers, and payment methods. This is the source for sales analytics, revenue trends, and later forecasting.

### 2. Raw Inventory Data

Inventory records are received in `data/raw/inventory/inventory.csv`. They contain products, categories, stock levels, reorder thresholds, and stores. This is the source for inventory monitoring and future replenishment recommendations.

### 3. Raw Customer Data

Customer records are received in `data/raw/customers/customers.csv`. They contain customer identifiers, profile attributes, cities, and registration dates. This is the source for customer history, segmentation, and later churn analysis.

### 4. Data Exploration

The data exploration stage profiles the raw datasets before transformation. It reports row and column counts, field names, data types, missing values, duplicate rows, numerical statistics, date coverage, and sales totals. The exploration script is read-only and does not change the raw files.

### 5. Data Cleaning

In a future preparation stage, data-quality rules will be applied to copies of the raw inputs. This stage may validate identifiers, dates, numeric values, duplicates, missing values, and relationships between datasets. Raw files remain preserved as the original source and are not overwritten.

### 6. Processed Data

The output of preparation will be consistent datasets suitable for analysis. Processed data will use agreed formats and validated relationships while retaining the business meaning of the source fields. The exact storage format and output locations will be defined when the cleaning requirements are approved.

### 7. Database

Processed sales, inventory, and customer data will be stored in a database for reliable querying and reuse. The database will support relationships between transactions, products, stores, and customers and provide a persistence layer for the future platform.

### 8. FastAPI Backend

The future FastAPI backend will expose application services and data endpoints to authorized platform clients. It will retrieve processed information and results from the database and provide a controlled interface for dashboards, reports, and business capabilities.

### 9. Business Analytics / AI Modules

Future business analytics and AI/ML modules will use the processed data and database services to provide:

- Sales analytics and inventory monitoring.
- Customer segmentation.
- Revenue forecasting.
- Product recommendations.
- Churn prediction.
- Anomaly detection.

These modules will produce metrics, forecasts, recommendations, risk indicators, and alerts for the reporting layer.

### 10. Dashboard / Reports

The future dashboard and reporting layer will present sales performance, inventory status, customer insights, forecasts, recommendations, churn results, and detected anomalies. Views and reports will be organized around the needs of the Business Owner, Store Manager, Sales Executive, and System Administrator.

## Data relationships

The three source datasets are connected through shared business identifiers:

- **Sales to Customers:** `sales.customer_id` links each sales record to `customers.customer_id`. This connection supports customer purchase history, segmentation, product recommendations, and churn prediction.
- **Sales to Inventory:** `sales.product_id` links a sold product to `inventory.product_id`. This connects sales demand and revenue with product stock information.
- **Sales to Inventory by store:** `sales.store_id` and `inventory.store_id` identify the store context. Together with `product_id`, they support store-level demand and stock analysis.
- **Product context:** `product_id`, `product_name`, and `category` provide product context in both Sales and Inventory. They support product and category performance analysis and future recommendations.

Customer attributes such as `age`, `gender`, `city`, and `registration_date` enrich sales transactions after the customer relationship is established. Inventory attributes such as `stock_level` and `reorder_threshold` add availability context to product demand.

## Milestone 1 boundary

At Day 1-2, the repository contains the raw CSV datasets, the read-only exploration script, and documentation of this planned flow. Data cleaning, processed-data storage, the database, FastAPI backend, business analytics, AI/ML modules, dashboards, and reports belong to later milestones and are not implemented here.
