# MarketMind AI: Low-Fidelity Wireframes

## Milestone 1, Day 3-4

These wireframes describe the planned screens and major information areas for MarketMind AI. They are design artifacts only. They do not implement React, authentication, RBAC, dashboards, APIs, or application behavior.

## 1. Login

```text
+--------------------------------------------------+
|                  MARKETMIND AI                  |
|             Small Business Intelligence         |
|                                                  |
|  +--------------------------------------------+  |
|  | Email                                      |  |
|  | [                                        ] |  |
|  | Password                                   |  |
|  | [                                        ] |  |
|  |                                            |  |
|  |              [ Sign In ]                   |  |
|  +--------------------------------------------+  |
|                                                  |
+--------------------------------------------------+
```

**Major sections:** Platform identity, email input, password input, and sign-in action. The authentication behavior is future work.

## 2. Business Owner Dashboard

```text
+--------------------------------------------------------------------------------+
| MarketMind AI | Business Owner                              [Reports] [Profile] |
+----------------------+---------------------------------------------------------+
| Navigation           | KPI CARDS                                               |
| - Overview           | [Revenue] [Units Sold] [Inventory] [Customers]          |
| - Sales              +---------------------------------------------------------+
| - Inventory          | SALES PERFORMANCE                                       |
| - Customers          | [Revenue and sales trend chart]                       |
| - Forecasts          +-----------------------------+---------------------------+
| - Reports            | INVENTORY MONITORING       | CUSTOMER INSIGHTS        |
|                      | [Stock and reorder view]   | [Segments and activity]  |
|                      +-----------------------------+---------------------------+
|                      | FORECASTS                 | ALERTS                   |
|                      | [Revenue forecast view]    | [Anomalies and churn]    |
|                      +-----------------------------+---------------------------+
|                      | REPORTS                                                       |
|                      | [Sales] [Inventory] [Customer] [AI/ML insight reports]      |
+----------------------+---------------------------------------------------------+
```

**Purpose:** Provide a business-wide view of revenue growth, sales performance, inventory, customer insights, forecasts, alerts, and reports.

## 3. Store Manager Dashboard

```text
+--------------------------------------------------------------------------------+
| MarketMind AI | Store Manager | Store: [Select]                 [Reports]       |
+----------------------+---------------------------------------------------------+
| Navigation           | KPI CARDS                                               |
| - Store Overview     | [Store Revenue] [Units Sold] [Low Stock] [Customers]    |
| - Sales              +---------------------------------------------------------+
| - Inventory          | STORE SALES                                             |
| - Forecasts          | [Daily/weekly sales performance]                      |
| - Reports            +-----------------------------+---------------------------+
|                      | INVENTORY STATUS           | FORECASTS                 |
|                      | [Stock by product]         | [Store revenue forecast]  |
|                      | [Reorder thresholds]       |                           |
|                      +-----------------------------+---------------------------+
|                      | ALERTS                    | REPORTS                   |
|                      | [Low stock and anomalies]  | [Store sales/inventory]   |
+----------------------+---------------------------------------------------------+
```

**Purpose:** Help a Store Manager monitor store sales, product availability, reorder needs, store forecasts, alerts, and operational reports.

## 4. Sales Executive Dashboard

```text
+--------------------------------------------------------------------------------+
| MarketMind AI | Sales Executive                              [Reports]          |
+----------------------+---------------------------------------------------------+
| Navigation           | KPI CARDS                                               |
| - My Sales           | [Revenue] [Transactions] [Active Customers] [Targets]   |
| - Customers          +---------------------------------------------------------+
| - Recommendations   | SALES ACTIVITY                                         |
| - Reports            | [Recent sales and revenue trend]                      |
|                      +-----------------------------+---------------------------+
|                      | CUSTOMER INSIGHTS         | RECOMMENDATIONS           |
|                      | [Customer history]        | [Recommended products]   |
|                      | [Customer segments]       |                           |
|                      +-----------------------------+---------------------------+
|                      | ALERTS                    | REPORTS                   |
|                      | [Churn-risk indicators]    | [Sales and customer]     |
+----------------------+---------------------------------------------------------+
```

**Purpose:** Help a Sales Executive understand customer activity, review segments, use product recommendations, monitor sales, and follow customer-related alerts and reports.

## 5. System Administrator Dashboard

```text
+--------------------------------------------------------------------------------+
| MarketMind AI | System Administrator                         [Profile]         |
+----------------------+---------------------------------------------------------+
| Navigation           | KPI CARDS                                               |
| - System Overview    | [Users] [Stores] [Data Sources] [System Status]         |
| - Users and Roles    +---------------------------------------------------------+
| - Data Status        | SYSTEM STATUS                                          |
| - Reports            | [Data ingestion and service status]                  |
|                      +-----------------------------+---------------------------+
|                      | USER AND ROLE STATUS       | DATA STATUS               |
|                      | [Users and role access]    | [Sales/inventory/customer]|
|                      |                            | [data status]             |
|                      +-----------------------------+---------------------------+
|                      | ALERTS                    | REPORTS                   |
|                      | [System and data alerts]   | [Operational reports]     |
+----------------------+---------------------------------------------------------+
```

**Purpose:** Provide the System Administrator with a high-level view of user and role configuration, data status, system status, alerts, and operational reports. The underlying authentication and RBAC implementation is future work.

## Wireframe scope

These layouts identify major sections only. Detailed interaction design, visual styling, responsive behavior, API integration, authentication, role enforcement, and dashboard implementation belong to later milestones.
