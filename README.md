# MarketMind AI

### AI-Powered Small Business Sales Forecasting & Revenue Growth Intelligence Platform

> **Milestone 1 — Foundation & Core Infrastructure**

---

## Project Overview

MarketMind AI helps small business owners understand their sales data, monitor inventory health, and grow revenue — without needing a data science team. The platform provides role-aware dashboards, real-time KPI monitoring, and lays the foundation for AI-driven forecasting in future milestones.

### Problem Statement

Small businesses generate large amounts of sales and transaction data but lack the tools to turn it into actionable intelligence. Spreadsheets are slow, generic BI tools are expensive, and hiring analysts isn't feasible. MarketMind AI solves this with an intelligent, role-aware platform that surfaces the right insights to the right people.

### Target Users

| Role                | What they need                                                    |
| ------------------- | ----------------------------------------------------------------- |
| **Owner / Admin**   | Full sales overview, transaction history, cross-store performance |
| **Store Manager**   | Inventory health, low-stock alerts, units-sold by product         |
| **Sales Executive** | Their own customer transactions (scoped to assigned customers)    |

---

## Milestone 1 Scope

This milestone establishes the full application foundation:

- [x] User authentication with JWT
- [x] Role-based access control (owner, admin, store_manager, sales_exec)
- [x] PostgreSQL database schema with SQLAlchemy ORM
- [x] REST API with FastAPI (sales transactions, inventory summary, transactions)
- [x] Data ingestion pipeline for two real datasets
- [x] Role-aware React frontend with live API integration
- [x] KPI dashboard (total units sold, total inventory, low-stock count)
- [x] Inventory management view (store manager role)
- [x] Sales transactions view (owner / admin role)

---

## Tech Stack

| Layer        | Technology                                    |
| ------------ | --------------------------------------------- |
| **Backend**  | Python 3.11+, FastAPI, SQLAlchemy, PostgreSQL |
| **Auth**     | JWT (python-jose), bcrypt (passlib)           |
| **Frontend** | React 19, Vite 5                              |
| **Data**     | Pandas (ETL pipeline)                         |

---

## Project Structure

```
marketmindAI/
├── backend/
│   ├── main.py           # FastAPI app — all routes
│   ├── models.py         # SQLAlchemy ORM models (User, Role, SalesTransaction, Transaction, Product, Customer)
│   ├── schemas.py        # Pydantic request/response schemas
│   ├── auth.py           # Password hashing, JWT creation/verification
│   ├── database.py       # SQLAlchemy engine setup
│   ├── init_db.py        # Creates all tables (run once)
│   ├── load_data.py      # ETL: loads prepped CSVs from ../datasets/processed into PostgreSQL
│   └── .env.example      # Environment variable template
├── frontend/
│   ├── src/
│   │   ├── App.jsx       # Main app — login, dashboard, role-aware views
│   │   ├── App.css       # Styles
│   │   ├── main.jsx      # React entry point
│   │   └── index.css     # Global CSS reset
│   ├── index.html
│   ├── vite.config.js
│   └── package.json
├── datasets/
│   ├── data_cleaning.py               # Day 5-6 cleaning/validation script — reads raw/, writes processed/
│   ├── raw/
│   │   ├── sales_data_final.csv
│   │   └── retail_sales_dataset_final.csv
│   └── processed/
│       ├── sales_data_prepped.csv         # loaded by backend/load_data.py
│       ├── retail_sales_data_prepped.csv  # loaded by backend/load_data.py
│       └── product_lookup.csv             # derived Product ID -> Category, see Data section
├── requirements.txt
├── .gitignore
└── README.md
```

---

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL running locally (or a connection string to a hosted instance)

---

### Backend Setup

```bash
cd backend

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# Install dependencies (requirements.txt is in the project root)
pip install -r ../requirements.txt

# Configure environment
cp .env.example .env
# Edit .env — set DATABASE_URL and SECRET_KEY

# Initialise the database (creates all tables)
python init_db.py

# Load sample data (reads prepped CSVs from ../datasets/processed — see Data section below)
python load_data.py

# Start the API server
uvicorn main:app --reload
# API runs at http://localhost:8000
# Interactive docs at http://localhost:8000/docs
```

---

### Frontend Setup

```bash
cd frontend

npm install
npm run dev
# App runs at http://localhost:5173
```

---

### Seed Roles & Users

After running `init_db.py`, seed the four roles directly in PostgreSQL (connect with `psql -U postgres -d marketmind`):

```sql
INSERT INTO roles (id, name) VALUES
('1', 'owner'),
('2', 'admin'),
('3', 'sales_exec'),
('4', 'store_manager');
```

`role_id` is a plain string column — any unique string works, but the app's existing test data and any future seed scripts assume these four values. Then register a test user per role via `POST /register`:

```json
{
  "name": "Test Owner",
  "email": "owner@test.com",
  "password": "test123",
  "role_id": "1"
}
```

---

## API Reference

All protected routes require `Authorization: Bearer <token>` header.

| Method | Path                  | Auth                        | Description                                             |
| ------ | --------------------- | --------------------------- | ------------------------------------------------------- |
| `POST` | `/register`           | Public                      | Create a new user                                       |
| `POST` | `/login`              | Public                      | Returns JWT access token                                |
| `GET`  | `/me`                 | Any logged-in user          | Current user profile + role                             |
| `GET`  | `/sales-transactions` | owner, store_manager, admin | Sales transaction list (limit 50)                       |
| `GET`  | `/transactions`       | owner, admin, sales_exec    | Transaction list (sales_exec sees only their customers) |
| `GET`  | `/sales/summary`      | owner, store_manager, admin | KPI totals: units sold, inventory, low-stock count      |
| `GET`  | `/admin-only`         | admin                       | Admin-only test route                                   |

---

## Data

Raw source files (`sales_data_final.csv`, `retail_sales_dataset_final.csv`) live in
`datasets/raw/` and are committed to the repository alongside the cleaned output, so the
full pipeline is reproducible end-to-end without needing external files. To regenerate
the prepped data from the raw files, run:

```bash
cd datasets
python data_cleaning.py
```

This runs the Day 5-6 checks (nulls, duplicates, range sanity checks — see the script
for the full exploration) and writes two cleaned CSVs into `datasets/processed/`:

| File                                               | Contents                                                                                 |
| -------------------------------------------------- | ---------------------------------------------------------------------------------------- |
| `datasets/processed/sales_data_prepped.csv`        | Store ID, Product ID, Date, Units Sold, Inventory Level, Demand                          |
| `datasets/processed/retail_sales_data_prepped.csv` | Customer ID, Gender, Age, Date, Product Category, Quantity, Price per Unit, Total Amount |
| `datasets/processed/product_lookup.csv`            | Product ID -> Category, one row per product (see note below)                             |

**On `product_lookup.csv` specifically:** the raw `sales_data_final.csv` has a real data
quality issue — the same Product ID shows up with 2-3 _different_ categories across rows
(confirmed for all 20 products, a synthetic-data generation artifact, not a few stray
typos). Since the `Product` table's primary key is `product_id`, only one category per
product can be stored. Resolved by taking the **most frequent category per Product ID**
(mode) rather than an arbitrary first-seen value — see the "2.5" section of
`data_cleaning.py` for the exact logic and reasoning.

`backend/load_data.py` reads all three files from `../datasets/processed/`. Just run it
from inside `backend/` as shown above.

---

## Role-Based Dashboard

After login the frontend detects the user's role from `/me` and renders the appropriate view:

**Owner / Admin** — Full sales transactions table with store, product, date, units sold, and inventory level.

**Store Manager** — Inventory overview sorted by stock level (ascending), with a "Reorder soon" status flag for items below 100 units.

**Sales Executive** — Placeholder view; full customer-scoped transaction history is planned for Milestone 2.

---

## Roadmap

| Milestone        | Focus                                                                  |
| ---------------- | ---------------------------------------------------------------------- |
| **M1 (current)** | Foundation: auth, RBAC, data ingestion, live API, role-aware dashboard |
| **M2**           | Sales forecasting with time-series models; sales_exec transaction view |
| **M3**           | AI-powered revenue growth recommendations and trend analysis           |
| **M4**           | Full forecasting UI, scenario simulation, exportable reports           |

---

## Contributing

This project is developed as part of the Infosys Springboard Virtual Internship Program 2026.

---

## License

MIT
