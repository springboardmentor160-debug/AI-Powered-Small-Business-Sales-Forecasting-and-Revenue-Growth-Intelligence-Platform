# MarketMind AI — Vercel Deployment & Live Platform Access

## 🌐 Live Production Application
- **Production URL:** [https://marketmind-wheat.vercel.app](https://marketmind-wheat.vercel.app)
- **Alternate Alias:** [https://marketmind-25am064-2262.vercel.app](https://marketmind-25am064-2262.vercel.app)
- **API Health Endpoint:** [https://marketmind-wheat.vercel.app/api/health](https://marketmind-wheat.vercel.app/api/health)
- **Hosting Platform:** Vercel (Edge Network + Python Serverless Runtime)
- **Deployment Status:** Active & Fully Operational (HTTP 200 OK)

---

## 👥 Demo Login Credentials (RBAC Roles)

The platform features full Role-Based Access Control (RBAC). You can sign in using any of the following pre-configured credentials or use the **"Demo Accounts"** one-click drawer on the login page:

| Role | Username / Email | Password | Access Scope |
| :--- | :--- | :--- | :--- |
| **Business Owner** | `owner@marketmind.ai` | `OwnerPass123!` | Executive KPIs, revenue forecasting, top-level analytics, data upload |
| **Store Manager** | `manager@marketmind.ai` | `ManagerPass123!` | Store-level operations, regional sales, inventory tracking |
| **Sales Executive** | `sales@marketmind.ai` | `SalesPass123!` | Customer RFM segmentation, individual customer profiles, churn risk |
| **Administrator** | `admin@marketmind.ai` | `AdminPass123!` | User management, RBAC controls, database audit logs & telemetry |

---

## 📱 Responsive Multi-Device Design
The deployed platform is optimized for both **Desktop / Laptop** and **Mobile / Tablet** environments:
- **Laptop & Desktop (width > 768px):** Wide executive header, persistent left navigation sidebar, 2-column comparative charts, detailed telemetry tables, and model configuration bars.
- **Mobile & Smartphones (width ≤ 768px):** Clean 2-row header (Row 1: Hamburger menu button + title; Row 2: Date period filter + compact action icons for Upload, Refresh, Avatar, and Logout), touch-friendly off-canvas drawer navigation with dim backdrop overlay, vertically-stacked responsive KPI cards, and independent horizontal scroll for data tables with zero page blowout.

---

## ⚙️ Technical Architecture on Vercel

```
marketmind-wheat.vercel.app
│
├── / (Static Frontend)
│   ├── index.html         # Executive Dashboard UI & Auth Modal
│   ├── index.css          # Design System with Desktop & Mobile Media Queries
│   └── app.js             # Client state management, Chart.js graphs, RBAC routing
│
├── /api/* (Serverless Backend)
│   ├── api/index.py       # ASGI entrypoint for Vercel Python Runtime
│   └── backend/           # FastAPI backend core
│       ├── main.py        # App initialization, CORS & route mounting
│       ├── routes.py      # Analytics, forecasting, inventory & upload endpoints
│       ├── auth.py        # JWT-based token generation & password hashing
│       ├── db_service.py  # Query aggregations & data caching
│       └── database.py    # Database connection with automated `/tmp` seeding
│
└── SQLite Database
    ├── marketmind.db      # 9,994 superstore transactions, pre-seeded users
    └── /tmp/marketmind.db # Writable database sandbox in Vercel Serverless environment
```

---

## 🚀 Key Platform Features
1. **Interactive Revenue Forecasting:** SARIMAX, Prophet, Random Forest, and XGBoost models with interactive date filters and horizon controls.
2. **Customer Intelligence & RFM:** Automatic customer segmentation (High Value, Regular, At-Risk, Dormant) with churn propensity scoring.
3. **Inventory & Product Intelligence:** Stock level alerts, reorder recommendations, and category profit margin heatmaps.
4. **Dataset Upload & Custom Ingestion:** Support for CSV and Excel (.xlsx) file uploads with instant validation, schema mapping, and real-time dashboard telemetry refresh.
5. **Automated Executive Reports:** Dynamic natural language summary generation with downloadable Markdown reports.
