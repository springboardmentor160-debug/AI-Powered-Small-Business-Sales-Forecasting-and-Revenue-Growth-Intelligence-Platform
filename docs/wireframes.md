# MarketMind AI — Dashboard Wireframes & UI Designs

This document presents low-fidelity wireframes and structural layouts for the **MarketMind AI** web client, covering the auth gateway and 4 role-specific views.

---

## 1. Authentication Wireframe (Login Screen)

```
+-----------------------------------------------------------------------+
|  MarketMind AI                                                        |
|  Small Business Sales Intelligence Platform                           |
+-----------------------------------------------------------------------+
|                                                                       |
|                     +---------------------------+                     |
|                     |        SIGN IN            |                     |
|                     |                           |                     |
|                     | Username / Email          |                     |
|                     | [ owner@marketmind.ai   ] |                     |
|                     |                           |                     |
|                     | Password                  |                     |
|                     | [ ********************  ] |                     |
|                     |                           |                     |
|                     | Select Role               |                     |
|                     | (o) Business Owner        |                     |
|                     | ( ) Store Manager         |                     |
|                     | ( ) Sales Executive       |                     |
|                     | ( ) Administrator         |                     |
|                     |                           |                     |
|                     | [   SIGN IN TO PORTAL   ] |                     |
|                     |                           |                     |
|                     | Demo credentials preview: |                     |
|                     | owner / manager / exec    |                     |
|                     +---------------------------+                     |
|                                                                       |
+-----------------------------------------------------------------------+
```

---

## 2. Business Owner Dashboard Wireframe

**Scope**: High-level strategic overview across all store branches.

```
+-----------------------------------------------------------------------+
| MarketMind AI | [Owner View]      Stores: All | User: CEO Owner [Logout] |
+-----------------------------------------------------------------------+
| [KPI] Total Sales | [KPI] Total Revenue | [KPI] Active Stores | [KPI] Low Stock |
|      $142,850     |       $142,850      |         3           |     4 Items     |
+-----------------------------------------------------------------------+
|                                  |                                    |
| [ Chart: Monthly Sales Trend ]   | [ Chart: Revenue by Category ]     |
|  $30k |    /\                    |  Electronics [========    ] 45%   |
|  $20k |  /    \    /\            |  Clothing    [====        ] 25%   |
|  $10k |/        \ /  \           |  Home        [===         ] 18%   |
|       +-------------------       |  Groceries   [==          ] 12%   |
|         Jan  Feb  Mar  Apr       |                                    |
+----------------------------------+------------------------------------+
| [ Table: Top Performing Products ]                                    |
| Product Name                   | Category     | Units Sold | Revenue  |
| Wireless Headphones            | Electronics  |    142     | $18,458  |
| Ergonomic Office Chair         | Home         |     89     | $17,755  |
| Running Shoes Pro              | Apparel      |    112     | $10,068  |
+-----------------------------------------------------------------------+
```

---

## 3. Store Manager Dashboard Wireframe

**Scope**: Detailed operational inventory and store-level sales performance.

```
+-----------------------------------------------------------------------+
| MarketMind AI | [Store Manager]   Branch: STORE-001 | User: Mgr [Logout]|
+-----------------------------------------------------------------------+
| [KPI] Store Sales | [KPI] Daily Txns | [KPI] Items Needing Reorder    |
|      $42,150      |       85         |          2 Alerts              |
+-----------------------------------------------------------------------+
| [ Inventory Alert Section: Reorder Threshold Triggered ]             |
| (!) Bluetooth Portable Speaker | Stock: 8 | Min Threshold: 12 [REORDER] |
| (!) Gaming Keyboard            | Stock: 5 | Min Threshold: 10 [REORDER] |
+-----------------------------------------------------------------------+
| [ Store Inventory Table & Real-Time Stock Status ]                    |
| SKU   | Product Name          | Category    | Price  | Stock | Action  |
| P101  | Wireless Headphones   | Electronics | $129.99|  45   | [Edit]  |
| P102  | Ergonomic Chair       | Home        | $199.50|  15   | [Edit]  |
| P107  | Bluetooth Speaker     | Electronics | $49.99 |   8*  | [Alert] |
+-----------------------------------------------------------------------+
```

---

## 4. Sales Executive Dashboard Wireframe

**Scope**: Front-line transaction logging and personal sales metrics.

```
+-----------------------------------------------------------------------+
| MarketMind AI | [Sales Executive]  Branch: STORE-001 | User: Exec [Logout]|
+-----------------------------------------------------------------------+
| [KPI] My Daily Sales | [KPI] Txns Processed | [KPI] Avg Order Value   |
|       $1,250.00      |          14          |         $89.28          |
+-----------------------------------------------------------------------+
| [ Quick New Sale Entry ]                                              |
| Product: [ Select Product v ]  Qty: [ 2 ]  Payment: [ Credit Card v ] |
| Customer ID: [ CUST-1004   ]               [ RECORD TRANSACTION ]     |
+-----------------------------------------------------------------------+
| [ My Recent Sales Log ]                                               |
| Transaction ID | Time     | Product           | Qty | Total  | Pay Method |
| TXN-10342      | 14:22:10 | Wireless Headphone|  1  | $129.99| Credit Card|
| TXN-10341      | 13:45:00 | Coffee Mug Set    |  2  | $59.90 | Cash       |
+-----------------------------------------------------------------------+
```

---

## 5. Administrator Control Panel Wireframe

**Scope**: User management, system health, audit logs, and data pipelines.

```
+-----------------------------------------------------------------------+
| MarketMind AI | [Administrator Panel]           | User: Admin [Logout] |
+-----------------------------------------------------------------------+
| [ System Status ] Backend API: ONLINE (12ms) | DB Status: OK (353 Rec) |
+-----------------------------------------------------------------------+
| [ User Management ]  [+ ADD NEW USER]                                 |
| User ID | Username   | Full Name      | Role        | Store     | Action |
| U101    | owner      | Executive CEO  | Owner       | Global    | [Edit] |
| U102    | mgr_ny     | Store Mgr NY   | Store Mgr   | STORE-001 | [Edit] |
| U103    | exec_sam   | Sam Exec       | Sales Exec  | STORE-001 | [Edit] |
+-----------------------------------------------------------------------+
| [ Pipeline Execution Logs ]                                           |
| 2026-08-26 21:30:00 [INFO] ETL Pipeline executed clean_data.py        |
| 2026-08-26 21:32:00 [INFO] Cleaned 350 transaction records successfully|
+-----------------------------------------------------------------------+
```
