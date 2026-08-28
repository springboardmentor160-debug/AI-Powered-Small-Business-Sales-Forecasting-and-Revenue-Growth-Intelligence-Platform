# MarketMind AI — Small Business Sales Intelligence Platform (Milestone 1)

MarketMind AI is a sales and inventory intelligence platform tailored for small and medium retail businesses. It centralizes Point-of-Sale (POS) transaction streams, cleans dirty data via Python data prep scripts, persists structured records in a relational database, and renders role-aware analytics dashboards via FastAPI and React.

---

## 📁 Repository Structure

```
marketmind-ai/
├── backend/                  # FastAPI Application & Data Prep Scripts
│   ├── data_prep/            # Python Data Pipeline
│   │   ├── generate_raw_data.py   # Synthetic raw POS data generator
│   │   ├── clean_data.py        # Data cleaning & deduplication engine
│   │   └── load_db.py           # Database seeder (schema + clean CSVs)
│   ├── routers/              # API Routers (sales, inventory, analytics)
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
│   ├── architecture.md       # Architecture spec & Mermaid system diagram
│   ├── data_dictionary.md    # Field dictionary & data cleaning rules
│   ├── db_schema.md          # ERD diagram & entity specification
│   ├── objectives.md         # Problem statement, target personas & data flow
│   └── wireframes.md         # Low-fi UI wireframes for auth & 4 dashboard roles
├── frontend/                 # React SPA Client (Vite + Recharts + Lucide)
│   ├── src/
│   │   ├── components/       # Header, KPICard, SalesChart, InventoryTable, etc.
│   │   ├── App.jsx           # Main Dashboard React Application
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
# Navigate to project root
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
- API Base URL: `http://localhost:8000`
- Interactive Swagger Docs: `http://localhost:8000/docs`

### Step 3: Start the React Frontend Application
```bash
# From project root:
cd frontend
npm install
npm run dev
```
- Client App URL: `http://localhost:3000`

---

## 🎯 Key Milestone 1 Completed Objectives

1. **Synthetic Data Generation & Data Cleaning Pipeline**: Generated realistic dirty POS records (`transaction_id`, `date`, `product_id`, `product_name`, `category`, `quantity`, `unit_price`, `total_amount`, `store_id`, `customer_id`, `payment_method`, `stock_level`, `reorder_threshold`) and cleaned formatting, duplicates, and missing values into normalized CSVs.
2. **Complete Documentation Suite**: `data_dictionary.md`, `objectives.md`, `architecture.md`, `db_schema.md`, `wireframes.md`.
3. **Database Layer**: SQLite relational database created with SQL schema definition (`db/schema.sql`).
4. **FastAPI Backend**: Routers for `/api/v1/analytics/summary`, `/api/v1/sales`, `/api/v1/inventory`.
5. **React SPA Frontend**: Beautiful dark mode UI with interactive Recharts charts, real-time KPI metrics, stock alert notifications, and role-based view switching.

---

## 🔒 Access Control (Pending Step)
Access Control stage (JWT Authentication + Role-Based Access Control enforcing permission boundaries for Business Owner, Store Manager, Sales Executive, Administrator) will be enabled next upon user approval.
