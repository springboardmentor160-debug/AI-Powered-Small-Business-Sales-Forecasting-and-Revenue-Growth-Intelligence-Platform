# MarketMind AI — Small Business Sales Intelligence Platform

MarketMind AI is an intelligent sales analytics and inventory monitoring platform designed to help small and medium-sized businesses (SMBs) extract actionable insights from their transactional data.

> **Milestone 1 Status**: **COMPLETE**  
> **Milestone 2 (Days 1–6) Status**: **COMPLETE**  
> Data Cleaning Pipeline, 3NF Relational Database, Idempotent Seeding, FastAPI Backend, JWT Authentication, Strict RBAC, React + Vite Dashboard, Customer Segmentation (K-Means K=4 & Hierarchical Agglomerative Clustering), 30-Day Prophet Sales Forecasting, Missing-Date Analysis, and Days 1–6 APIs & UI components are fully operational and verified.


---

## Table of Contents
1. [Overview & Core Features](#overview--core-features)
2. [Technology Stack](#technology-stack)
3. [Repository Structure](#repository-structure)
4. [Role-Based Access Control (RBAC)](#role-based-access-control-rbac)
5. [Demo User Accounts](#demo-user-accounts)
6. [Quickstart & Setup Instructions (Windows)](#quickstart--setup-instructions-windows)
7. [API Catalog & Swagger UI](#api-catalog--swagger-ui)
8. [Automated Verification & Testing](#automated-verification--testing)
9. [Milestone 2 Roadmap](#milestone-2-roadmap)

---

## Overview & Core Features

- **Data Quality Pipeline**: Automated ingestion and cleaning of raw sales records, handling missing quantities/customers, duplicates, negative values, and date format normalization.
- **Relational Data Foundation**: A normalized 6-table SQLite database modeled with SQLAlchemy ORM (`users`, `customers`, `products`, `sales`, `inventory`, `invoices`).
- **Idempotent Seeding**: Re-running database loader scripts guarantees exactly **8 validated sales transactions** without creating duplicate records.
- **RESTful API Services**: FastAPI backend exposing structured endpoints for sales metrics, inventory alerts, business analytics, and administrative management.
- **JWT & Password Security**: Secure authentication powered by `bcrypt` password hashing and `PyJWT` stateless bearer tokens. Python 3.13 compliant.
- **Role-Tailored Dashboards**: High-performance React 19 + Vite dashboard featuring dynamic SVG revenue trend charts, KPI cards, real-time inventory alerts, and role-specific workspace views.

---

## Technology Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Backend Framework** | FastAPI 0.115+ | High-performance asynchronous REST API |
| **ASGI Server** | Uvicorn 0.30+ | Production-grade server engine |
| **ORM & Database** | SQLAlchemy 2.0+ / SQLite 3 | Normalized relational schema & transactions |
| **Data Processing** | Pandas 3.0+ | Exploration, profiling, and preprocessing |
| **Security & Auth** | PyJWT & bcrypt | JWT bearer authorization & cryptographic hashing |
| **Frontend Framework** | React 19 + Vite 8 | Fast single-page application (SPA) |
| **Frontend Styling** | Modern Vanilla CSS | Custom glassmorphism design system & responsive layout |

---

## Repository Structure

```text
marketmind-ai/
├── backend/
│   ├── __init__.py               # Backend package initialization
│   ├── main.py                   # FastAPI app entrypoint, CORS, routes
│   ├── database.py               # SQLite connection & SessionLocal provider
│   ├── models.py                 # SQLAlchemy ORM models (6 tables)
│   ├── schemas.py                # Pydantic request & response schemas
│   ├── auth.py                   # Bcrypt hashing & PyJWT token utilities
│   ├── dependencies.py           # FastAPI dependency guards (get_current_user, RBAC)
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── auth.py               # Login, registration, /me endpoints
│   │   ├── sales.py              # Sales list & summary calculations
│   │   ├── inventory.py          # Inventory stock & low-stock alerts
│   │   ├── analytics.py          # Dashboard KPIs, sales trends, top products
│   │   └── users.py              # User management (strictly Admin protected)
│   ├── data_exploration.py       # Raw dataset profiling & anomaly detection
│   ├── data_cleaning.py          # Cleaning script producing 8 verified records
│   ├── create_db.py              # Table schema creation
│   ├── load_data.py              # Idempotent database population
│   ├── check_database.py         # DB verification script
│   ├── test_api.py               # Comprehensive 17-point automated API test suite
│   └── requirements.txt          # Python dependencies
├── data/
│   ├── raw/
│   │   └── sales_data.csv        # Original raw sales data (14 records)
│   └── processed/
│       └── clean_sales_data.csv  # Validated sales records (8 clean records)
├── db/
│   └── marketmind.db             # Relational SQLite database
├── docs/
│   ├── objectives.md             # Problem statement, scope, user personas
│   ├── architecture.md           # System architecture, data flow & Mermaid diagrams
│   ├── data_dictionary.md        # Comprehensive field definitions & types
│   ├── db_schema.md              # Table definitions, constraints & Mermaid ERD
│   └── wireframes.md             # Low-fidelity UI screen wireframes
├── frontend/
│   ├── index.html                # HTML entrypoint with Inter Google font
│   ├── package.json              # React dependencies
│   ├── vite.config.js            # Vite configuration with /api backend proxy
│   └── src/
│       ├── main.jsx              # React mounting script
│       ├── App.jsx               # Auth state manager & role dispatcher
│       ├── api.js                # Fetch API client with Bearer token injector
│       ├── index.css             # Glassmorphism design tokens & styles
│       ├── components/
│       │   ├── Navbar.jsx        # Branding, active user badge & sign out
│       │   ├── KPICard.jsx       # Metric cards with accent colors
│       │   ├── SalesChart.jsx    # SVG area/line sales trend visualization
│       │   ├── SalesTable.jsx    # Searchable sales transaction table
│       │   ├── InventoryAlerts.jsx # Low-stock alerts with deficit calculations
│       │   └── PlannedFeaturesNotice.jsx # Transparent Milestone 2 roadmap note
│       └── pages/
│           ├── LoginPage.jsx     # Login card with 1-click Demo Account helpers
│           ├── OwnerDashboard.jsx # Strategic business performance dashboard
│           ├── ManagerDashboard.jsx # Inventory & replenishment operations dashboard
│           ├── SalesDashboard.jsx # Orders, customers & invoice workspace
│           └── AdminDashboard.jsx # User directory & live RBAC isolation tester
├── .gitignore
└── README.md
```

---

## Role-Based Access Control (RBAC)

| Role | Dashboard Perspective | Access Permissions | Restricted Areas |
|---|---|---|---|
| **Business Owner** (`owner`) | Strategic Business Performance | Full sales KPIs, daily trends, top products, inventory alert summaries | User management, AI model configuration |
| **Store Manager** (`manager`) | Inventory & Store Operations | Stock catalog, reorder threshold alerts, daily fulfillments | User management, AI model configuration |
| **Sales Executive** (`sales_executive`) | Sales Representative Workspace | Customer accounts, orders, invoices, individual metrics | Inventory management, user management, strategic forecasting |
| **System Administrator** (`admin`) | Security & Governance Console | Full system access, platform user directory (`/api/v1/users`), RBAC verification | None (Unrestricted) |

---

## Demo User Accounts

All demo accounts share the default password: **`password123`**. The login page provides **Instant 1-Click Demo Buttons** for rapid testing:

| Role | Username Alias | Email Address | Password |
|---|---|---|---|
| **Business Owner** | `owner` | `owner@marketmind.ai` | `password123` |
| **Store Manager** | `manager` | `manager@marketmind.ai` | `password123` |
| **Sales Executive** | `exec` | `exec@marketmind.ai` | `password123` |
| **System Administrator** | `admin` | `admin@marketmind.ai` | `password123` |

---

## Quickstart & Setup Instructions (Windows)

### 1. Prerequisites
- Python 3.11+ (Python 3.13.14 fully tested and supported)
- Node.js 18+ and npm

### 2. Activate Virtual Environment & Install Dependencies
Open a PowerShell terminal at the repository root:
```powershell
# Activate the existing virtual environment
.venv\Scripts\activate

# Install Python backend dependencies
pip install -r backend\requirements.txt
```

### 3. Clean Data & Initialize Database
```powershell
# Run data exploration
python -m backend.data_exploration

# Run data cleaning (creates data/processed/clean_sales_data.csv with 8 clean rows)
python -m backend.data_cleaning

# Create SQLite database tables
python -m backend.create_db

# Load data idempotently (seeds users, customers, products, sales, inventory, invoices)
python -m backend.load_data

# Verify database health and exact 8 sales records
python -m backend.check_database
```

### 4. Start the FastAPI Backend
```powershell
python -m uvicorn backend.main:app --reload --port 8000
```
- API Base URL: `http://127.0.0.1:8000`
- Interactive OpenAPI Swagger Docs: `http://127.0.0.1:8000/docs`

### 5. Start the React Frontend
Open a new terminal window:
```powershell
cd frontend
npm install
npm run dev
```
- React Application URL: **`http://localhost:5173/`**

---

## API Catalog & Swagger UI

FastAPI automatically generates interactive Swagger documentation available at `http://127.0.0.1:8000/docs`.

### Key Endpoints:
- `GET /` — API health check (`{"message": "MarketMind AI API is running"}`)
- `POST /api/v1/auth/login` — Authenticate via username/email & password; returns JWT token
- `POST /api/v1/auth/register` — Create new user account with role validation
- `GET /api/v1/auth/me` — Return current authenticated user profile
- `GET /api/v1/sales` — List all 8 verified sales transactions with customer/product data
- `GET /api/v1/sales/summary` — Aggregate revenue ($697.00), orders (8), units (29), AOV ($87.12)
- `GET /api/v1/inventory` — Product catalog with stock on hand and reorder points
- `GET /api/v1/inventory/alerts` — Low stock items (`stock_level < reorder_point`)
- `GET /api/v1/analytics/summary` — Full dashboard metrics (KPIs, trend chart data, top products)
- `GET /api/v1/users` — System user directory (**Strictly Admin only — Returns 403 for non-admins**)
- `GET /api/v1/segmentation/summary` — Customer segmentation summary metrics ($K=4$ K-Means & Hierarchical)
- `GET /api/v1/segmentation/customers` — Segmented customer table with cluster IDs & segment names
- `GET /api/v1/forecasting/summary` — 30-day Prophet sales forecast with uncertainty bounds & missing dates check

---

## Automated Verification & Testing

To execute the automated 17-point API test suite for Milestone 1:
```powershell
$env:PYTHONPATH="."; .venv\Scripts\python.exe backend/test_api.py
```

To execute the automated test suite for Milestone 2 (Days 1–6):
```powershell
$env:PYTHONPATH="."; .venv\Scripts\python.exe backend/test_milestone2.py
```


Expected output:
```text
========== RUNNING BACKEND API TESTS ==========
PASS: 1. GET / health check
PASS: 2. POST /api/v1/auth/login (Owner)
PASS: 3. POST /api/v1/auth/login (Manager)
PASS: 4. POST /api/v1/auth/login (Sales Executive)
PASS: 5. POST /api/v1/auth/login (Admin)
PASS: 6. POST /api/v1/auth/login rejected on wrong password (401)
PASS: 7. GET /api/v1/auth/me authenticated
PASS: 8. GET /api/v1/sales returned exactly 8 sales records
PASS: 9. GET /api/v1/sales/summary verified: Revenue=$697.0, Orders=8, Units=29, Top Product='Marker Box'
PASS: 10. GET /api/v1/inventory returned 4 items
PASS: 11. GET /api/v1/inventory/alerts found 2 low-stock items: ['Pen Set', 'Marker Box']
PASS: 12. GET /api/v1/analytics/summary verified with charts and KPI data
PASS: 13. GET /api/v1/users successfully returned 4 users for Admin
PASS: 14. GET /api/v1/users rejected for Owner (403 Forbidden)
PASS: 15. GET /api/v1/users rejected for Manager (403 Forbidden)
PASS: 16. GET /api/v1/users rejected for Sales Exec (403 Forbidden)
PASS: 17. Unauthenticated request to protected endpoint rejected (401)

========== ALL 17 BACKEND API TESTS PASSED! ==========
```

---

## Milestone 2 Roadmap

The foundation laid in Milestone 1 prepares MarketMind AI for the upcoming predictive intelligence milestones:
- **Milestone 2**: Prophet and XGBoost time-series sales forecasting, K-Means customer segmentation (RFM analysis), and customer churn prediction models.
- **Milestone 3**: Collaborative filtering product recommendations, Isolation Forest anomaly/fraud detection, and natural language executive querying.