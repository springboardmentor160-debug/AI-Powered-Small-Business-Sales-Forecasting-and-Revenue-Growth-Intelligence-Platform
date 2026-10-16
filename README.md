# MarketMind AI — Small Business Sales Intelligence Platform

MarketMind AI is an enterprise-grade sales forecasting, inventory intelligence, and customer segmentation platform designed specifically for small-to-medium retail operations. It ingests messy Point-of-Sale (POS) transaction streams, runs automated ETL data cleaning, stores structured records in a relational database, applies machine learning models (Prophet, Random Forest, XGBoost, and K-Means/Hierarchical Clustering), and delivers real-time intelligence via an interactive Streamlit dashboard backed by a secure FastAPI REST API.

---

## 🏛️ System Architecture

```mermaid
flowchart TD
    subgraph Data Layer
        A[Raw Dirty POS CSVs] -->|Data Prep ETL| B[Data Cleaner]
        B -->|Normalized Records| C[(SQLite / Relational DB)]
    end

    subgraph Intelligence Engine
        C -->|Daily Series| D[Sales Forecasting: Prophet / RF / XGBoost]
        C -->|RFM Profiles| E[Customer Segmentation: K-Means & Agglomerative]
        D --> F[Recursive 30-Day Projections]
        E --> G[4 Centroid-Named Behavioral Segments]
        F & G --> H[Executive Excel Report Generator]
    end

    subgraph Backend API (FastAPI)
        C & F & G & H --> I[FastAPI REST Gateway]
        I --> J[RBAC Auth Middleware / JWT Verification]
    end

    subgraph User Experience (Streamlit)
        I --> K[Streamlit Intelligence Suite]
        K --> L[POS Overview & Simulator]
        K --> M[Interactive 3D/2D Customer Clusters]
        K --> N[Sales Forecast Visualizer with Bounds]
        K --> O[Real-Time Reorder Alerts]
        K --> P[User & RBAC Administration]
    end
```

---

## 🔐 Role-Based Access Control (RBAC) Matrix

| Platform Feature / Endpoint | Business Owner | Store Manager | Sales Executive | Administrator |
| :--- | :---: | :---: | :---: | :---: |
| **POS Sales KPIs (`/api/v1/analytics/summary`)** | ✅ Full Access | 🏬 Store-Isolated (`STORE-001`) | 👤 Personal Sales | ✅ Full Access |
| **Customer Segmentation (`/segments`)** | ✅ Full Access | ✅ Full Access | ✅ Full Access | ✅ Full Access |
| **Customer ID Verification (`/api/v1/customers/{id}`)** | ✅ Full Access | ✅ Full Access | ✅ Full Access | ✅ Full Access |
| **Sales Forecasting (`/forecast/revenue`, `/forecast/series`)** | ✅ Full Access | 👁️ View Only | ❌ **Restricted (403 Forbidden)** | ✅ Full Access |
| **Excel Business Report (`/reports/business`)** | ✅ Full Access | 👁️ View/Download | ❌ **Restricted (403 Forbidden)** | ✅ Full Access |
| **User Administration (`/api/v1/users`)** | ❌ No Access | ❌ No Access | ❌ No Access | ✅ Full Access |

### Default Demo User Credentials
- **Business Owner**: `owner` / `password123`
- **Store Manager**: `manager` / `password123`
- **Sales Executive**: `exec` / `password123`
- **Administrator**: `admin` / `password123`

---

## 🚀 How to Run Locally

### 1. Prerequisites
- Python 3.10+ (tested on Python 3.11 & 3.14)
- Git

### 2. Setup & Virtual Environment
```bash
# Clone the repository
git clone https://github.com/springboardmentor160-debug/AI-Powered-Small-Business-Sales-Forecasting-and-Revenue-Growth-Intelligence-Platform.git
cd AI-Powered-Small-Business-Sales-Forecasting-and-Revenue-Growth-Intelligence-Platform

# Create and activate virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt
```

### 3. Initialize Database & Run Precomputations (Optional — Auto-runs on Startup)
```bash
python backend/data_prep/clean_data.py
python backend/data_prep/load_db.py
python backend/ml/train.py
```

### 4. Start the Application

#### Option A: Running Services Individually
```bash
# Terminal 1 — Start FastAPI Backend:
python -m uvicorn backend.main:app --port 8000 --reload

# Terminal 2 — Start Streamlit Frontend:
streamlit run app.py --server.port 8501
```

#### Option B: Unified Runner (Free-Tier 512MB RAM Friendly)
```bash
python start_unified.py
```

- **Streamlit Frontend Dashboard**: [http://localhost:8501](http://localhost:8501)
- **FastAPI API Swagger Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Health Check Endpoint**: [http://localhost:8000/health](http://localhost:8000/health)

---

## 🐳 Running with Docker & Docker Compose

```bash
# Build and spin up both containers
docker compose up --build -d

# Check running status
docker compose ps

# View live container logs
docker compose logs -f

# Shut down
docker compose down
```

---

## ☁️ Cloud Deployment (Vercel, Render & Railway)

- **Live Production Deployment (Vercel)**: **[https://dist-one-wine-30.vercel.app](https://dist-one-wine-30.vercel.app)**
- **Render**: Connect repository, use `start_unified.py` as start command, and select Free plan (512MB RAM).
- **Railway**: Deploy directly using the provided `railway.json` and `Procfile`.
- **Full Deployment Documentation**: Available in [docs/deployment_guide.md](file:///D:/Infosys/docs/deployment_guide.md).

---

## 📡 REST API Reference

| Method | Endpoint | Description | Access Scope |
| :--- | :--- | :--- | :--- |
| `GET` | `/health` | Healthcheck returning DB connection status | Public |
| `POST` | `/api/v1/auth/login` | OAuth2 password login generating JWT | Public |
| `GET` | `/api/v1/analytics/summary` | POS sales KPIs and category breakdowns | Authenticated (Store-isolated) |
| `POST` | `/api/v1/sales/` | Record POS transactions with stock deduction | Authenticated |
| `GET` | `/api/v1/customers/{id}` | Customer profile lookup (returns 404 if missing) | Authenticated |
| `GET` | `/segments` | RFM cluster breakdown and segment metrics | Authenticated |
| `GET` | `/segments/customers` | Searchable, paginated customer profiles | Authenticated |
| `GET` | `/forecast/revenue` | Multi-horizon projected revenue and metrics | Owner, Manager, Admin (403 for Exec) |
| `GET` | `/forecast/series` | Historical + forecasted revenue series with bounds | Owner, Manager, Admin (403 for Exec) |
| `GET` | `/reports/business` | Formatted multi-sheet Excel report download | Owner, Manager, Admin (403 for Exec) |
| `GET` | `/api/v1/users/` | User account administration | Administrator Only |

---

## 🧪 Running the Automated Test Suite

```bash
# Run all pytest test suites
python -m pytest tests/ -v

# Run Phase A integration verification script
python scratch/test_phase_a_checklist.py
```
