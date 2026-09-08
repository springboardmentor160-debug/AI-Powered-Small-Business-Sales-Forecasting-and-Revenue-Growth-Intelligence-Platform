# MarketMind AI — Data Dictionary

This document describes all data fields across the raw dataset, the cleaned dataset, and the normalized database entities.

---

## 1. Raw Sales Dataset (`data/raw/sales_data.csv`)

| Column | Data Type | Nullable | Description | Observed Quality Issues |
|---|---|---|---|---|
| `order_id` | Integer | No | Transaction reference identifier | Duplicate order ID `1009` |
| `product_name` | String | No | Name of the purchased product | Inconsistent casing across items |
| `quantity` | Float / Int | Yes | Quantity purchased | Missing value in row 8 (order `1007`); negative value in row 12 (order `1010`) |
| `unit_price` | Float | No | Unit price per item in USD | Zero unit price in row 14 (order `1012`) |
| `order_date` | String | No | Date order was placed | Non-standard format `11/01/2026` in row 13 (order `1011`) |
| `customer_id` | String | Yes | Customer reference code | Missing customer ID in row 15 (order `1013`) |

---

## 2. Cleaned Sales Dataset (`data/processed/clean_sales_data.csv`)

| Column | Data Type | Nullable | Validation Constraints | Description |
|---|---|---|---|---|
| `order_id` | Integer | No | Unique, positive integer | Validated order identifier (exactly 8 unique rows) |
| `product_name` | String | No | Non-empty string | Validated product name |
| `quantity` | Float | No | `quantity > 0` | Validated positive quantity sold |
| `unit_price` | Float | No | `unit_price > 0.0` | Validated positive price in USD |
| `order_date` | String (YYYY-MM-DD) | No | Standard ISO-8601 date | Normalized calendar date |
| `customer_id` | String | No | Non-empty string | Validated customer reference |
| `total_amount` | Float | No | `quantity * unit_price` | Calculated total line transaction value |

---

## 3. Relational Database Tables (`db/marketmind.db`)

### Table: `users`
Stores application user accounts for authentication and role-based access control.

| Field | Type | Constraints | Description |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY, AUTOINCREMENT | System surrogate identifier |
| `name` | VARCHAR(100) | NOT NULL | User full display name |
| `email` | VARCHAR(120) | NOT NULL, UNIQUE, INDEX | Login email address |
| `password_hash` | VARCHAR(255) | NOT NULL | One-way bcrypt cryptographic hash |
| `role` | VARCHAR(50) | NOT NULL | Access role: `owner`, `manager`, `sales_executive`, `admin` |
| `created_at` | DATETIME | NOT NULL | UTC account creation timestamp |

---

### Table: `customers`
Stores business customer master data.

| Field | Type | Constraints | Description |
|---|---|---|---|
| `id` | VARCHAR(50) | PRIMARY KEY, INDEX | Customer code (e.g., `C001`, `C002`) |
| `name` | VARCHAR(120) | NOT NULL | Customer business or commercial name |
| `contact_info` | VARCHAR(200) | NULLABLE | Primary email contact address |

---

### Table: `products`
Stores product catalog information and baseline unit prices.

| Field | Type | Constraints | Description |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY, AUTOINCREMENT, INDEX | Product surrogate identifier |
| `name` | VARCHAR(120) | NOT NULL, UNIQUE | Standard product name |
| `category` | VARCHAR(80) | NOT NULL | Product category (e.g., `Stationery`, `Writing Instruments`) |
| `unit_price` | REAL | NOT NULL, `> 0.0` | Baseline unit catalog price in USD |

---

### Table: `sales`
Stores sales order transactions linked to products and customers.

| Field | Type | Constraints | Description |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY, AUTOINCREMENT, INDEX | Internal sales record identifier |
| `order_id` | INTEGER | NOT NULL, UNIQUE, INDEX | Business order ID from POS/CSV |
| `product_id` | INTEGER | NOT NULL, FOREIGN KEY -> `products.id` | Reference to purchased product |
| `customer_id` | VARCHAR(50) | NOT NULL, FOREIGN KEY -> `customers.id` | Reference to purchasing customer |
| `quantity` | INTEGER | NOT NULL, `> 0` | Units purchased |
| `unit_price` | REAL | NOT NULL, `> 0.0` | Transacted unit price in USD |
| `sale_date` | DATE | NOT NULL | Date of the transaction |

---

### Table: `inventory`
Tracks current stock levels and replenishment trigger points for products.

| Field | Type | Constraints | Description |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY, AUTOINCREMENT, INDEX | Inventory record surrogate identifier |
| `product_id` | INTEGER | NOT NULL, UNIQUE, FOREIGN KEY -> `products.id` | Reference to catalog product |
| `stock_level` | INTEGER | NOT NULL, `>= 0` | Current units available on hand |
| `reorder_point` | INTEGER | NOT NULL, `>= 0` | Threshold below which low-stock alert triggers |

---

### Table: `invoices`
Records payment and billing state for every sales order.

| Field | Type | Constraints | Description |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY, AUTOINCREMENT, INDEX | Invoice record surrogate identifier |
| `sale_id` | INTEGER | NOT NULL, UNIQUE, FOREIGN KEY -> `sales.id` | Reference to sales transaction |
| `amount` | REAL | NOT NULL, `>= 0.0` | Total invoiced transaction amount |
| `payment_status`| VARCHAR(50) | NOT NULL | Current status (`PAID`, `PENDING`) |
