# MarketMind AI — Small Business Sales Intelligence Platform (Milestone 1)

MarketMind AI is an enterprise-grade sales and inventory intelligence platform tailored for small and medium retail businesses. It centralizes Point-of-Sale (POS) transaction streams, cleans dirty data via automated Python ETL pipelines, persists structured records in a relational database, and renders role-aware analytics dashboards via FastAPI and React.

---

## 📁 Repository Structure

```
marketmind-ai/
├── backend/                  # FastAPI Application & Data Prep Engine
│   ├── data_prep/            # Python Data Pipeline
│   │   ├── generate_raw_data.py   # Synthetic raw POS data generator
│   │   ├── clean_data.py        # Data cleaning & deduplication engine
│   │   └── load_db.py           # Database seeder (schema + clean CSVs)
│   ├── routers/              # API Routers (auth, users, sales, inventory, analytics)
│   │   ├── auth.py              # JWT authentication endpoints (login, register, me)
│   │   ├── users.py             # User administration endpoints (RBAC)
│   │   ├── sales.py             # Sales transaction endpoints
│   │   ├── inventory.py         # Inventory & reorder stock endpoints
│   │   └── analytics.py         # Summary metrics & category breakdown
│   ├── auth.py               # Security module (Bcrypt hashing, PyJWT tokens, RBAC dependencies)
│   ├── database.py           # SQLAlchemy Connection Engine
│   ├── main.py               # FastAPI Web Entrypoint
│   ├── models.py             # SQLAlchemy ORM Models
│   ├── schemas.py            # Pydantic Schemas
│   └── requirements.txt      # Python dependencies
├── data/                     # Raw & Processed Datasets
│   ├── raw/                  # Dirty POS CSV exports
│   └── processed/            # Cleaned sales & inventory CSVs
├── db/                       # Database Schema & SQLite Storage
│   ├── schema.sql            # ANSI / SQLite DDL Schema Definition
│   └── marketmind.db         # SQLite database file
├── docs/                     # System & Design Documentation
│   ├── architecture.md       # Architecture spec & Mermaid sequence/system diagrams
│   ├── data_dictionary.md    # Field dictionary & data cleaning rules
│   ├── db_schema.md          # ERD diagram & entity specification
│   ├── objectives.md         # Problem statement, target personas & data flow
│   └── wireframes.md         # Low-fi UI wireframes for auth & 4 dashboard roles
├── frontend/                 # React SPA Client (Vite + Recharts + Lucide Icons)
│   ├── src/
│   │   ├── components/       # Header, KPICard, SalesChart, InventoryTable, LoginModal, etc.
│   │   ├── App.jsx           # Main Dashboard React Application & Role Router
│   │   ├── index.css         # Modern dark-mode & glassmorphism CSS design system
│   │   └── main.jsx          # React DOM entrypoint
│   ├── package.json          # Node dependencies
│   └── vite.config.js        # Vite build configuration
├── .gitignore
└── README.md
```

---

## 🚀 How to Run Locally

### Prerequisites
- **Python 3.10+**
- **Node.js 18+** & **npm**

### Step 1: Initialize Database & Run Data Prep Pipeline
```bash
# From project root
python backend/data_prep/generate_raw_data.py
python backend/data_prep/clean_data.py
python backend/data_prep/load_db.py
```

### Step 2: Train ML Models & Generate Artifacts (Optional — Auto-runs on API Startup)
```bash
# From project root:
python backend/ml/train.py
```

### Step 3: Start the FastAPI Backend Server
```bash
# From project root:
python -m uvicorn backend.main:app --reload --port 8000
```
- **API Base URL**: `http://localhost:8000`
- **Interactive Swagger Docs**: `http://localhost:8000/docs`

### Step 4: Start the Streamlit Intelligence Dashboard
```bash
# From project root:
streamlit run app.py --server.port 8501
```
- **Dashboard Application URL**: `http://localhost:8501`

---

## 🔐 Default Demo Accounts (JWT Authentication & RBAC)

When launched, the client application displays a sleek JWT login portal with pre-configured shortcut logins:

| Role | Username | Password | Access Scope |
| :--- | :--- | :--- | :--- |
| **Business Owner** | `owner` | `password123` | **Global View**: Access to overall revenue, net sales trends, customer segments, 30-day forecast, report downloads. |
| **Store Manager** | `manager` | `password123` | **Store View**: Enforced store isolation (`STORE-001`), stock replenishment alerts, forecast view. |
| **Sales Executive** | `exec` | `password123` | **Terminal View**: Personal sales logs, customer segments; **Forecast Reports restricted (403)**. |
| **Administrator** | `admin` | `password123` | **Control Center**: User administration (`/api/v1/users`), RBAC provisioning, forecasting and system audit. |

---

## 📋 Wireframe-to-Endpoint Tracking Table

| Wireframe Section / Feature | Backend Endpoint | Status |
| :--- | :--- | :--- |
| **Sales Today / Top Products** | `/api/v1/analytics/summary`, `/api/v1/sales` | Built in Milestone 1 |
| **Customer Segments Panel** | `/segments`, `/segments/customers` | Built in Milestone 2 |
| **Sales Trend / Forecast** | `/forecast/revenue`, `/forecast/series` | Built in Milestone 2 |
| **Low Stock Alerts** | `/inventory/alerts` | Still pending |
| **Recommendation Panel** | `/recommendations` | Comes in Milestone 3 |
| **Executive Excel Business Report** | `/reports/business` | Built in Milestone 2 |
| **Authentication & RBAC Gateway** | `/api/v1/auth/login`, `/api/v1/auth/me` | Built in Milestone 1 |
| **User Administration Panel** | `/api/v1/users` | Built in Milestone 1 |

---

## 🎯 Milestone 2 Completed Stages

- [x] **Customer Segmentation**: RFM feature extraction (`purchase_frequency`, `purchase_value`, `customer_activity_days` anchored to dataset max date + 1 day), StandardScaler, K-Means (K=4) + Hierarchical Agglomerative clustering, dendrogram (`artifacts/dendrogram.png`), programmatic centroid-based naming ("VIP / Loyal Customers", "Regular Customers", "Occasional Shoppers", "At-Risk / Fading Customers"), and ARI + silhouette validation.
- [x] **Sales Forecasting**: Daily revenue series aggregation with missing date detection, leak-free feature engineering (`shift(1)` before rolling), 80/20 chronological split, same-window benchmark across Prophet, Random Forest, and XGBoost, programmatic winner selection (Prophet), and recursive 30-day ahead projections with confidence intervals.
- [x] **Executive Reporting**: Professional multi-sheet Excel report (`artifacts/business_report.xlsx`) generated via openpyxl with Rupee (`₹`) formatting, styled headers, and clean business terminology.
- [x] **Backend & RBAC Integration**: New routes `/segments`, `/segments/customers`, `/forecast/revenue`, `/forecast/series`, `/reports/business` protected with `require_role`. Strict 403 Forbidden enforcement for Sales Executive on forecast and reports.
- [x] **Streamlit Intelligence Dashboard**: Production UI with custom dark theme (`.streamlit/config.toml` + CSS), role-aware access controls, Plotly interactive charts, KPI cards, and Excel report download.
