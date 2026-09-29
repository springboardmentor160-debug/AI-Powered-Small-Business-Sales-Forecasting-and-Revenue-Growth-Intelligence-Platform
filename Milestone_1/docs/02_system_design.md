                         ┌──────────────┐
                         │     USER     │
                         └──────┬───────┘
                                │
                                ▼
                    ┌─────────────────────┐
                    │       ReactJS       │
                    │      Frontend       │
                    │     Dashboard       │
                    └──────────┬──────────┘
                               │
                            REST API
                               │
                               ▼
                    ┌─────────────────────┐
                    │       FastAPI       │
                    │       Backend       │
                    │  APIs + Business    │
                    │       Logic         │
                    └───────┬─────┬───────┘
                            │     │
                            │     ▼
                            │ ┌─────────────────────────┐
                            │ │       AI / ML Layer     │
                            │ │                         │
                            │ │ Prophet → Sales        │
                            │ │           Forecasting  │
                            │ │                         │
                            │ │ K-Means → Customer     │
                            │ │           Segmentation │
                            │ │                         │
                            │ │ Random Forest → Churn  │
                            │ │                 Prediction│
                            │ │                         │
                            │ │ Anomaly Detection →     │
                            │ │ Unusual Transactions    │
                            │ └────────────┬────────────┘
                            │              │
                            ▼              ▼
                    ┌──────────────────────────┐
                    │       PostgreSQL         │
                    │         Database         │
                    │                          │
                    │ Customers | Products     │
                    │ Geography | Orders       │
                    └──────────────────────────┘



Database structure

| Table | Key Fields | Connects To (Foreign Key) |
| --- | --- | --- |
| users | id, name, email, role | None |
| customers | id, name, segment, region | None |
| products | id, name, category, unit_price | None |
| sales | id, product_id, customer_id, quantity, sales_amount, sale_date | products(id), customers(id) |
| inventory | id, product_id, stock_level, reorder_point | products(id) |
| invoices | id, sale_id, amount, payment_status | sales(id) |

SQL DDL Script (postgreSQL)

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    role VARCHAR(50) NOT NULL
);

CREATE TABLE customers (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    segment VARCHAR(50),
    region VARCHAR(50)
);

CREATE TABLE products (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(50),
    unit_price DECIMAL(10, 2)
);

CREATE TABLE sales (
    id SERIAL PRIMARY KEY,
    product_id VARCHAR(50) REFERENCES products(id),
    customer_id VARCHAR(50) REFERENCES customers(id),
    quantity INTEGER NOT NULL,
    sales_amount DECIMAL(10, 2) NOT NULL,
    sale_date DATE NOT NULL
);

CREATE TABLE inventory (
    id SERIAL PRIMARY KEY,
    product_id VARCHAR(50) REFERENCES products(id),
    stock_level INTEGER DEFAULT 100,
    reorder_point INTEGER DEFAULT 20
);

CREATE TABLE invoices (
    id SERIAL PRIMARY KEY,
    sale_id INTEGER REFERENCES sales(id),
    amount DECIMAL(10, 2) NOT NULL,
    payment_status VARCHAR(50) DEFAULT 'Paid'
);

Dashboard UI framework

+-----------------------------------------------------------------------+
|  MarketMind AI                        [Store: Central] [User Profile] |
+-----------------------------------------------------------------------+
|  [ Sales Today ]       [ Low Stock Alerts ]      [ Top Product ]      |
|    $45,200                   3 items                Tech / Phones     |
+-----------------------------------------------------------------------+
|  SALES TREND (Last 30 Days)           |  AI RECOMMENDATION PANEL      |
|                                       |  - Restock Product X (Low)    |
|  [ Line Chart: Revenue vs Date ]      |  - Promote Category Y (High)  |
|                                       |                               |
+---------------------------------------+-------------------------------+
|  CUSTOMER SEGMENTS                    |  ACTION / EXPORTS             |
|  - Consumer: 52%                      |  [ Export CSV Report ]        |
|  - Corporate: 30%                     |  [ Refresh Data ]             |
|  - Home Office: 18%                   |                               |
+-----------------------------------------------------------------------+




