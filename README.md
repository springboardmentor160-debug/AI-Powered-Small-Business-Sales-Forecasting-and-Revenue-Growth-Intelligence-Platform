# MarketMind — Restaurant Chain Revenue & Stock Intelligence Platform

MarketMind centralizes order data across a multi-outlet restaurant/cloud-kitchen
chain, cleans dirty POS-style exports through a Python ETL pipeline, stores
structured records in SQLite, and renders role-aware, colorful analytics
dashboards via FastAPI and React.

This project follows the same general shape as a retail sales-intelligence
reference project (POS transactions → ETL → RBAC dashboards) but is
re-scoped to a restaurant-chain domain (outlets, menu items, orders, patrons)
with its own schema, API surface, and a distinct sidebar-based, colorful
dashboard UI.

---

## 📁 Repository Structure

```
marketmind/
├── backend/                      # FastAPI application & data pipeline
│   ├── data_prep/
│   │   ├── generate_raw_orders.py   # Synthetic "dirty" order data generator
│   │   ├── clean_orders.py          # Cleans dates/categories/payment modes
│   │   └── seed_db.py               # Seeds roles, outlets, staff, menu, orders
│   ├── routers/
│   │   ├── auth.py                  # JWT login + /me
│   │   ├── staff.py                 # Staff administration (RBAC, admin-only)
│   │   ├── menu.py                  # Menu items & stock levels
│   │   ├── orders.py                # Order history & order placement
│   │   └── insights.py              # Revenue/analytics summary
│   ├── auth.py                   # Bcrypt hashing, JWT issuing, RoleChecker
│   ├── database.py                # SQLAlchemy engine/session
│   ├── main.py                    # FastAPI entrypoint
│   ├── models.py                  # ORM models
│   ├── schemas.py                 # Pydantic schemas
│   └── requirements.txt
├── data/
│   ├── raw/                       # Generated "dirty" CSV exports
│   └── processed/                 # Cleaned CSVs used to seed the DB
├── db/
│   ├── schema.sql                 # DDL reference
│   └── marketmind.db                 # SQLite database (pre-seeded)
├── frontend/                      # React SPA (Vite + Recharts + lucide-react)
│   └── src/
│       ├── components/            # Sidebar, KpiGrid, CategoryChart, tables...
│       ├── App.jsx                # Dashboard router
│       ├── index.css              # Colorful/vibrant design system
│       └── main.jsx
└── README.md
```

---

## 🚀 Running Locally

### Prerequisites
- Python 3.10+
- Node.js 18+ and npm

### 1. Data pipeline (already run once — `db/marketmind.db` ships pre-seeded)
```bash
cd backend
python data_prep/generate_raw_orders.py
python data_prep/clean_orders.py
python data_prep/seed_db.py
```

### 2. Backend
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8000
```
- API base: `http://localhost:8000`
- Swagger docs: `http://localhost:8000/docs`

### 3. Frontend
```bash
cd frontend
npm install
npm run dev
```
- App: `http://localhost:3000` (proxies `/api/v1` to the backend)

---

## 🔐 Demo Accounts (JWT + RBAC)

| Role | Username | Password | Access Scope |
| :--- | :--- | :--- | :--- |
| **Franchise Owner** | `owner` | `password123` | Global view — revenue, orders, top items across every outlet |
| **Outlet Manager** | `manager` | `password123` | Locked to `OUT-BBSR` — stock alerts, restock management |
| **Waiter** | `waiter` | `password123` | Locked to `OUT-BBSR` — order entry, quick menu lookup |
| **Admin** | `admin` | `password123` | Staff administration (`/api/v1/staff`) |

---

## 🎨 What's different from the reference project

- **Domain**: restaurant/cloud-kitchen chain (outlets, menu items, patrons,
  orders) instead of generic retail POS (stores, inventory, customers,
  transactions).
- **Schema & API**: renamed entities/fields throughout (`Staff` not `User`,
  `MenuItem` not `Inventory`, `Order` not `Transaction`, `/api/v1/insights`
  not `/api/v1/analytics`, etc.) and a simplified 4-role set.
- **UI**: sidebar navigation (not a top header), a warm/vibrant gradient
  color system (coral/violet/teal/amber) instead of dark glassmorphism,
  gradient KPI cards, and a different component set.
