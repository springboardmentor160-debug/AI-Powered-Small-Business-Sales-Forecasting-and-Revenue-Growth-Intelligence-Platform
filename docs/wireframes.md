# MarketMind AI — UI Wireframes (Low-Fidelity)

This document presents low-fidelity text/ASCII mockups for the primary screens across all 4 system roles.

---

## 1. Authentication Screen (`LoginPage`)

```text
+-------------------------------------------------------------------------+
|                                                                         |
|                          MARKETMIND AI                                  |
|               Small Business Sales Intelligence Platform                |
|                                                                         |
|         +-----------------------------------------------------+         |
|         |                     Sign In                         |         |
|         |                                                     |         |
|         |  Username / Email:                                  |         |
|         |  [ owner@marketmind.ai                           ]  |         |
|         |                                                     |         |
|         |  Password:                                          |         |
|         |  [ **********                                    ]  |         |
|         |                                                     |         |
|         |  [            LOG IN TO DASHBOARD                ]  |         |
|         |                                                     |         |
|         |  ----------------- Quick Demo Accounts ------------  |         |
|         |  [ Owner ]    [ Manager ]    [ Sales Exec ]  [ Admin]|         |
|         +-----------------------------------------------------+         |
|                                                                         |
+-------------------------------------------------------------------------+
```

---

## 2. Business Owner Dashboard (`OwnerDashboard`)

```text
+-------------------------------------------------------------------------+
| MarketMind AI  [Role: Business Owner] [owner@marketmind.ai]   [ Logout ]|
+-------------------------------------------------------------------------+
|  Overview & Strategic Business Performance                              |
|                                                                         |
|  +---------------+  +---------------+  +---------------+  +------------+|
|  | TOTAL REVENUE |  | TOTAL ORDERS  |  |  UNITS SOLD   |  |  AVG ORDER ||
|  |    $697.00    |  |       8       |  |      29       |  |   $87.12   ||
|  +---------------+  +---------------+  +---------------+  +------------+|
|                                                                         |
|  +-----------------------------------+  +------------------------------+|
|  | Daily Sales Trend Chart (Jan 2026)|  | Top Revenue Products         ||
|  | $150 |       *                    |  | 1. Marker Box     $240.00    ||
|  | $100 |   *       *                |  | 2. Notebook A     $180.00    ||
|  |  $50 | *             *            |  | 3. Pen Set        $192.00    ||
|  |   $0 +------------------------    |  | 4. Stapler        $ 85.00    ||
|  |      05  06  07  08  09  10       |  |                              ||
|  +-----------------------------------+  +------------------------------+|
|                                                                         |
|  +---------------------------------------------------------------------+|
|  | Low-Stock Alerts Overview                                           ||
|  | ! Pen Set: 10 in stock (Reorder point: 15)                          ||
|  | ! Marker Box: 6 in stock (Reorder point: 12)                        ||
|  +---------------------------------------------------------------------+|
|                                                                         |
|  [!] Milestone 2 Roadmap: AI Sales Forecasting & Churn Prediction      |
+-------------------------------------------------------------------------+
```

---

## 3. Store Manager Dashboard (`ManagerDashboard`)

```text
+-------------------------------------------------------------------------+
| MarketMind AI  [Role: Store Manager]  [manager@marketmind.ai] [ Logout ]|
+-------------------------------------------------------------------------+
|  Store Inventory & Daily Operations                                     |
|                                                                         |
|  +---------------------------------------------------------------------+|
|  | !! LOW STOCK ATTENTION REQUIRED (2 Alerts)                          ||
|  | - Pen Set: Stock 10 / Reorder Point 15 -> Deficit: -5 units         ||
|  | - Marker Box: Stock 6 / Reorder Point 12 -> Deficit: -6 units       ||
|  +---------------------------------------------------------------------+|
|                                                                         |
|  Product Stock Inventory Catalog:                                       |
|  +------------+--------------------+-------+---------+--------+--------+|
|  | Product    | Category           | Price | In Stock| Reorder| Status ||
|  +------------+--------------------+-------+---------+--------+--------+|
|  | Notebook A | Stationery         | $45.00|   45    |   20   | HEALTHY||
|  | Pen Set    | Writing Instruments| $12.00|   10    |   15   | ALERT  ||
|  | Marker Box | Stationery         | $30.00|    6    |   12   | ALERT  ||
|  | Stapler    | Office Equipment   | $85.00|   28    |   10   | HEALTHY||
|  +------------+--------------------+-------+---------+--------+--------+|
|                                                                         |
|  Recent Orders Log: (Order ID, Product, Qty, Date)                      |
+-------------------------------------------------------------------------+
```

---

## 4. Sales Executive Dashboard (`SalesDashboard`)

```text
+-------------------------------------------------------------------------+
| MarketMind AI  [Role: Sales Exec]     [exec@marketmind.ai]    [ Logout ]|
+-------------------------------------------------------------------------+
|  Sales Transactions & Customer Accounts                                 |
|                                                                         |
|  +---------------+  +---------------+  +---------------+                |
|  | TRANSACTIONS  |  | CUSTOMERS MET |  | TOTAL BILLED  |                |
|  |       8       |  |       5       |  |    $697.00    |                |
|  +---------------+  +---------------+  +---------------+                |
|                                                                         |
|  Sales Transactions Table:                                              |
|  +--------+------------+-----+--------+------------+-------------------+|
|  | Order# | Product    | Qty | Total  | Date       | Customer          ||
|  +--------+------------+-----+--------+------------+-------------------+|
|  | 1001   | Notebook A |  3  | $135.00| 2026-01-05 | Acme Corporation  ||
|  | 1002   | Pen Set    | 10  | $120.00| 2026-01-05 | Apex Retailers    ||
|  | 1003   | Notebook A |  1  | $ 45.00| 2026-01-06 | Acme Corporation  ||
|  | 1004   | Marker Box |  5  | $150.00| 2026-01-07 | Beta Enterprises  ||
|  | ...    | ...        | ... | ...    | ...        | ...               ||
|  +--------+------------+-----+--------+------------+-------------------+|
+-------------------------------------------------------------------------+
```

---

## 5. System Administrator Dashboard (`AdminDashboard`)

```text
+-------------------------------------------------------------------------+
| MarketMind AI  [Role: Administrator]  [admin@marketmind.ai]   [ Logout ]|
+-------------------------------------------------------------------------+
|  System Administration & User Access Control (RBAC)                     |
|                                                                         |
|  System Status: ONLINE  | API: Healthy  | DB: SQLite Active (6 Tables)  |
|                                                                         |
|  Platform User Accounts Management:                                     |
|  +----+----------------------+-----------------------+-----------------+|
|  | ID | Full Name            | Email Address         | System Role     ||
|  +----+----------------------+-----------------------+-----------------+|
|  | 1  | Business Owner       | owner@marketmind.ai   | owner           ||
|  | 2  | Store Manager        | manager@marketmind.ai | manager         ||
|  | 3  | Sales Executive      | exec@marketmind.ai    | sales_executive ||
|  | 4  | System Administrator | admin@marketmind.ai   | admin           ||
|  +----+----------------------+-----------------------+-----------------+|
|                                                                         |
---

## 6. Wireframe-to-Endpoint Tracking

| Wireframe Component | Backend API Endpoint | Status |
|---|---|---|
| **Sales Today / Top Product** | `/sales/summary` (`/api/v1/sales/summary`) | Built in Milestone 1 |
| **Customer Segments Panel** | `/segments` (`/api/v1/segmentation/segments`) | Built in Milestone 2 |
| **Sales Trend / Forecast** | `/forecast/revenue` (`/api/v1/forecasting/revenue`) | Built in Milestone 2 |
| **Forecast Model Comparison** | `/forecast/models` (`/api/v1/forecasting/models`) | Built in Milestone 2 |
| **Low Stock Alerts** | `/inventory/alerts` (`/api/v1/inventory/alerts`) | Built in Milestone 1 |
| **Recommendation Panel** | `/recommendations` | Milestone 3 |

### Text Summary:
- **Sales Today / Top Product**: `/sales/summary` — Built in Milestone 1
- **Customer Segments Panel**: `/segments` — Built in Milestone 2
- **Sales Trend / Forecast**: `/forecast/revenue` — Built in Milestone 2
- **Forecast Model Comparison**: `/forecast/models` — Built in Milestone 2
- **Low Stock Alerts**: `/inventory/alerts` — Built in Milestone 1
- **Recommendation Panel**: `/recommendations` — Milestone 3

