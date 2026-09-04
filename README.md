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

### Step 2: Start the FastAPI Backend Server
```bash
# From project root:
cd backend
python -m uvicorn main:app --reload --port 8000
```
- **API Base URL**: `http://localhost:8000`
- **Interactive Swagger Docs**: `http://localhost:8000/docs`

### Step 3: Start the React Frontend Application
```bash
# From project root:
cd frontend
npm install
npm run dev
```
- **Client Application URL**: `http://localhost:3000`

---

## 🔐 Default Demo Accounts (JWT Authentication & RBAC)

When launched, the client application displays a sleek JWT login portal with pre-configured shortcut logins:

| Role | Username | Password | Access Scope |
| :--- | :--- | :--- | :--- |
| **Business Owner** | `owner` | `password123` | **Global View**: Access to overall revenue, net sales trends, top performing products, cross-store metrics. |
| **Store Manager** | `manager` | `password123` | **Store View**: Enforced store isolation (`STORE-001`), stock replenishment alerts, SKU stock management. |
| **Sales Executive** | `exec` | `password123` | **Terminal View**: Personal / terminal sales logs, quick product pricing & availability lookup. |
| **Administrator** | `admin` | `password123` | **Control Center**: User administration (`/api/v1/users`), RBAC provisioning, infrastructure logs. |

---

## 🎯 Milestone 1 Completed Stages

- [x] **Data & Objectives**: Generated realistic dirty POS records (`transaction_id, date, product_id, product_name, category, quantity, unit_price, total_amount, store_id, customer_id, payment_method, stock_level, reorder_threshold`), wrote `data_dictionary.md` and `objectives.md`.
- [x] **Design**: Authored `architecture.md`, `db_schema.md`, `schema.sql`, and `wireframes.md`.
- [x] **Data Prep**: Developed Python ETL scripts (`generate_raw_data.py`, `clean_data.py`, `load_db.py`) and populated `marketmind.db`.
- [x] **Initial Build**: Set up FastAPI backend routers and React single-page frontend application with responsive charts and card components.
- [x] **Access Control**: Implemented JWT authentication (`POST /api/v1/auth/login`), password hashing, RBAC middleware, store-level data isolation, and user management (`/api/v1/users`).
- [x] **GitHub**: Structured git commit history following stage progression, root README.md, and `.gitignore`.
