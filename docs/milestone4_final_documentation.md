# MarketMind AI — Milestone 4 Final Comprehensive Documentation

**Project Title:** MarketMind AI — Small Business Sales Forecasting & Revenue Growth Intelligence Platform  
**Target Milestone:** Milestone 4 (Final Milestone)  
**Git Branch:** `feature/milestone-4-sultan`  
**Evaluation Persisted Artifact:** `reports/milestone4_test_results.csv`  
**Evaluation Report:** `reports/milestone4_evaluation_report.md`  

---

## 1. Project Overview

**MarketMind AI** is an enterprise-grade sales intelligence and decision-support web application tailored for small businesses and retail managers. It combines modern full-stack web engineering with applied machine learning to deliver actionable revenue forecasting, customer segmentation, churn risk intelligence, collaborative product recommendations, and real-time transaction anomaly detection.

Milestone 4 completes the platform through formal mathematical benchmarking across all five AI engines, end-to-end integration polish, production Docker containerization, cloud deployment readiness, and a unified automated test suite.

---

## 2. Architecture and Technology Stack

MarketMind AI employs a decoupled, multi-tier client-server architecture:

```
[React 19 + Vite Frontend SPA] (Port 5173 / Port 80)
             │
             │ HTTPS / JSON API + JWT
             ▼
[FastAPI REST Backend] (Port 8000)
     ├── Authentication & RBAC (JWT + Bcrypt)
     ├── Routers: Auth, Sales, Inventory, Analytics, Users,
     │            Segmentation, Forecasting, Recommendations,
     │            Churn, Anomalies, Evaluation
     ├── ML Engine Services (pandas, scikit-learn, Prophet, XGBoost, mlxtend)
     └── SQLite Database (db/marketmind.db via SQLAlchemy ORM)
```

### Core Technologies
- **Backend:** Python 3.13, FastAPI 0.115+, Uvicorn (ASGI)
- **Frontend:** React 19, Vite 8, Vanilla CSS Design System with dark mode and glassmorphism
- **Database:** SQLite 3 with SQLAlchemy 2.0 ORM
- **Machine Learning & Analytics:**
  - *Time-Series Forecasting:* Facebook Prophet 1.1.5, Random Forest Regressor, XGBoost Regressor
  - *Clustering:* Scikit-learn K-Means, Agglomerative Hierarchical Clustering, Scipy linkage dendrograms
  - *Churn Classification:* Logistic Regression, Random Forest Classifier, XGBoost Classifier
  - *Recommendation System:* Cosine similarity collaborative filtering, MLxtend Apriori association rules
  - *Anomaly Detection:* Statistical Z-Score, Scikit-learn Isolation Forest
- **Containerization & Deployment:** Docker, Docker Compose, Multi-stage builds with Nginx reverse proxy, Render Blueprint (`render.yaml`)

---

## 3. Milestone 1–3 Functionality Preserved

All functionality delivered across earlier milestones remains fully functional and verified:
- **Milestone 1:**
  - Cleaned retail sales transaction dataset (8 verified records across 5 customers).
  - SQLite database persistence with relational models: `User`, `SalesRecord`, `InventoryItem`.
  - JWT authentication with secure password hashing (`bcrypt`).
  - Role-Based Access Control (RBAC) across 4 roles: Business Owner, Store Manager, Sales Executive, System Administrator.
- **Milestone 2:**
  - Dynamic RFM-style customer segmentation into 4 business personas (*VIP / Loyal*, *Regular*, *Occasional*, *At-Risk / Fading*).
  - Multi-model time-series forecasting (Prophet, Random Forest, XGBoost) with 30-day revenue projections and prediction intervals.
  - Multi-tab Excel business report generator (`reports/business_report.xlsx`).
- **Milestone 3:**
  - Hybrid product recommender combining collaborative filtering and association rule mining with cold-start fallbacks.
  - Churn intelligence engine classifying customer retention risk into High, Medium, and Low tiers.
  - Multi-method transaction anomaly detection (1D statistical Z-scores and 3D Isolation Forest).

---

## 4. Artificial Intelligence Modules Overview

1. **Sales Forecasting Engine:** Predicts daily sales revenue for the next 30 days. Uses strict temporal train/test split without future data leakage (`shift(1)` rolling statistics). Automatically selects the model with the lowest prediction error.
2. **Customer Segmentation Engine:** Clusters customer purchase habits using scaled frequency, total monetary value, and customer activity span. Generates hierarchical dendrograms and assigns intuitive business segment labels.
3. **Churn Intelligence Engine:** Calculates behavioral recency from transaction inactivity, trains binary classifiers, predicts individual churn probabilities, and prioritizes recall to prevent lost customer lifetime value.
4. **Product Recommendation Engine:** Suggests unpurchased items by identifying behavioral peer customers (cosine similarity) and co-purchase patterns (Apriori confidence and lift).
5. **Transaction Anomaly Detector:** Flags high-outlier orders, zero-quantity anomalies, and unusual multidimensional feature combinations for human managerial review.

---

## 5. Model Evaluation Methodology & Actual Results

### 5.1 Measured Performance Summary (from `reports/milestone4_test_results.csv`)

| Module | Evaluated Models | Primary Metrics | Observed Results | Sample Size & Notes |
|---|---|---|---|---|
| **Sales Forecasting** | Prophet, Random Forest, XGBoost | MAE, RMSE, $R^2$ | **Prophet (Champion):** Test MAE 21.73, Test RMSE 21.73.<br>**RF:** Test MAE 25.96.<br>**XGBoost:** Test MAE 83.49 (Overfitting: Train MAE 0.28). | 5 daily records (4 train, 1 test). Test $R^2$ is mathematically `unavailable` on 1 observation. |
| **Customer Segmentation** | K-Means ($k=4$), Hierarchical ($k=4$) | Silhouette Score | **K-Means:** 0.3215<br>**Hierarchical:** 0.3215<br>$k=2$ sensitivity: 0.6506 | 5 customer profiles. $k=5$ degenerate case correctly recorded as `unavailable`. |
| **Churn Prediction** | Logistic Regression, Random Forest, XGBoost | Accuracy, Precision, Recall, F1 | **All Models:** Recall 100%, Precision 50%, F1 0.6667, Accuracy 50%. | Held-out test partition ($N=2$, 1 churned, 1 active). Zero false negatives achieved. |
| **Product Recommendations** | Hybrid Engine | Precision@3, Recall@3 | **Precision@3:** 0.0000<br>**Recall@3:** 0.0000 | Evaluated on 3 multi-order customers via leave-one-out. Catalog repeat-buys suppressed by novelty filter. |
| **Anomaly Detection** | Z-Score ($z=2.0$), Isolation Forest ($c=0.20$) | Detection Accuracy, FPR | **Isolation Forest:** Accuracy 100%, FPR 0.0%<br>**Z-Score:** Accuracy 90%, FPR 0.0% | Evaluated on isolated test fixture ($N=20$: 16 normal, 4 injected anomalies). |

### 5.2 Scientific Honesty & Dataset Reality Disclosures
- **Small Sample Constraints:** The repository contains a compact retail dataset (8 transaction lines, 5 customers). Metrics reflect genuine executions on this data rather than fabricated production scales.
- **XGBoost Overfitting:** Evaluation clearly demonstrated that complex tree ensembles overfit on small time-series samples (Train MAE 0.28 vs Test MAE 83.49), justifying Prophet's automated selection as champion.
- **Recommendation Specifics:** Small-business customers in this dataset repeated single product purchases. Because discovery recommenders intentionally exclude already-purchased products, Precision@3 was 0.0. This demonstrates metric integrity.
- **Isolated Anomaly Fixture:** Unlabeled business transactions were not falsely labeled as fraud. Detector behavior was instead validated on a separate, dedicated test fixture (`data/test_fixtures/anomaly_eval_fixture.csv`).

---

## 6. Local Installation & Startup Instructions

### 6.1 Prerequisites
- Python 3.13 (or 3.11+)
- Node.js 20+ and npm 10+
- Git

### 6.2 Environment Setup
Clone the repository and switch to the Milestone 4 branch:
```bash
git checkout feature/milestone-4-sultan
```

Copy the environment configuration template:
```bash
cp .env.example .env
```

### 6.3 Backend Setup & Startup
Activate the Python virtual environment and run the FastAPI server:
```bash
# In project root:
.venv\Scripts\activate          # On Windows
# or: source .venv/bin/activate  # On Linux/macOS

# Start FastAPI server on port 8000:
uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```
The backend API is accessible at: `http://127.0.0.1:8000`  
Interactive Swagger documentation: `http://127.0.0.1:8000/docs`

### 6.4 Frontend Setup & Startup
In a separate terminal, install dependencies and start the Vite development server:
```bash
cd frontend
npm install
npm run dev
```
The frontend application is accessible at: `http://localhost:5173`

---

## 7. Automated Testing Instructions

To run the complete automated test suite across all milestones using pytest:
```bash
# From project root:
.venv\Scripts\python -m pytest
```

### Test Suite Execution Output
```text
collected 13 items

backend\test_api.py .                                                    [  7%]
backend\test_milestone2.py .                                             [ 15%]
backend\test_milestone3.py .                                             [ 23%]
backend\test_milestone4.py ..........                                    [100%]

======================= 13 passed, 4 warnings in 25.49s =======================
```

To run individual milestone test modules:
```bash
.venv\Scripts\python -m pytest backend/test_milestone4.py -v
.venv\Scripts\python -m pytest backend/test_milestone3.py -v
.venv\Scripts\python -m pytest backend/test_milestone2.py -v
.venv\Scripts\python -m pytest backend/test_api.py -v
```

---

## 8. Docker Containerization Setup

MarketMind AI is fully containerized using multi-stage Docker builds and Docker Compose.

### 8.1 Docker Artifacts Created
- `backend/Dockerfile`: Python 3.13-slim with gcc/build-essential, non-root user considerations, healthcheck on `/health`, and Uvicorn runtime.
- `frontend/Dockerfile`: Multi-stage build (Node 20 Alpine builder + Nginx 1.25 Alpine runner).
- `frontend/nginx.conf`: Nginx SPA routing with reverse-proxying of `/api`, `/forecast`, `/segments`, `/recommendations`, `/churn`, and `/anomalies` to backend.
- `docker-compose.yml`: Coordinates services, health dependencies, and persistent volume mounts (`./db:/app/db`, `./reports:/app/reports`).
- `.dockerignore`: Prevents virtual environments, secrets, and caches from entering build contexts.

### 8.2 Docker Commands
```bash
# Validate configuration:
docker compose config

# Build container images:
docker compose build

# Start services in background:
docker compose up -d

# View container logs:
docker compose logs -f

# Verify running services:
docker compose ps

# Stop containers:
docker compose down
```

*Note on Local Environment:* Docker is currently not installed on the local Windows host. The container configuration has been constructed to industry specifications and can be executed immediately upon installing Docker Desktop.

---

## 9. Cloud Deployment Guide (Render)

### 9.1 Provider Recommendation: Render
**Render** was selected as the primary cloud provider because:
1. It natively supports Python 3.13 web services with persistent disk mounts for SQLite (`/app/db`).
2. It offers free static site hosting for Vite/React applications.
3. Infrastructure can be deployed as code via the included `render.yaml` blueprint.

### 9.2 Step-by-Step Render Deployment
1. **Push Changes to GitHub:** Push `feature/milestone-4-sultan` to your remote repository.
2. **Log into Render:** Connect your GitHub account at `https://dashboard.render.com`.
3. **Deploy Blueprint:**
   - Click **New +** -> **Blueprint**.
   - Select your repository and point to `render.yaml`.
   - Render will provision two services: `marketmind-api` (Web Service) and `marketmind-frontend` (Static Site).
4. **Environment Variables in Render Dashboard:**
   - `JWT_SECRET_KEY`: Set to a strong random 32-character string.
   - `DATABASE_URL`: `sqlite:///./db/marketmind.db`
   - `PYTHONPATH`: `.`
5. **Verify Public Endpoints:**
   - Backend Health: `https://<your-backend-subdomain>.onrender.com/health`
   - Frontend Dashboard: `https://<your-frontend-subdomain>.onrender.com`

---

## 10. API Endpoints & Role-Based Access Control (RBAC)

### 10.1 Role Permissions Matrix

| Endpoint | Method | Owner | Manager | Sales Exec | Admin |
|---|---|:---:|:---:|:---:|:---:|
| `/api/v1/auth/login` | POST | ✅ | ✅ | ✅ | ✅ |
| `/api/v1/sales` | GET | ✅ | ✅ | ✅ | ✅ |
| `/api/v1/inventory` | GET | ✅ | ✅ | ❌ (403) | ✅ |
| `/api/v1/analytics/summary` | GET | ✅ | ✅ | ❌ (403) | ✅ |
| `/api/v1/users` | GET | ❌ (403) | ❌ (403) | ❌ (403) | ✅ |
| `/api/v1/forecasting/summary` | GET | ✅ | ✅ | ❌ (403) | ✅ |
| `/api/v1/forecasting/report` | GET | ✅ | ✅ | ❌ (403) | ✅ |
| `/api/v1/segmentation/summary` | GET | ✅ | ✅ | ❌ (403) | ✅ |
| `/api/v1/recommendations/{cid}` | GET | ✅ | ✅ | ❌ (403) | ✅ |
| `/api/v1/churn` | GET | ✅ | ✅ | ❌ (403) | ✅ |
| `/api/v1/anomalies` | GET | ✅ | ✅ | ❌ (403) | ✅ |
| `/api/v1/evaluation/summary` | GET | ✅ | ✅ | ❌ (403) | ✅ |
| `/api/v1/evaluation/run` | POST | ✅ | ❌ (403) | ❌ (403) | ✅ |
| `/api/v1/evaluation/download-csv` | GET | ✅ | ✅ | ❌ (403) | ✅ |

### 10.2 Default Demonstration Credentials
- **Business Owner:** `username: owner`, `password: password123`
- **Store Manager:** `username: manager`, `password: password123`
- **Sales Executive:** `username: exec`, `password: password123`
- **System Administrator:** `username: admin`, `password: password123`

---

## 11. Final End-to-End Demonstration Checklist

Follow this checklist during final evaluator walkthroughs:

1. **Authentication:**
   - Log in as `owner` -> Land on Owner Executive Dashboard.
   - Verify role badge reads "Strategic Access".
2. **Sales Analytics:**
   - Inspect Total Revenue (₹697.00), Total Orders (8), and Top Selling Products.
3. **Milestone 4 Formal AI Model Evaluation Hub:**
   - View top summary cards (Forecasting Champion Prophet, Silhouette 0.3215, Churn Recall 100%, Anomaly Accuracy 100%).
   - Click filter tabs: *Sales Forecasting*, *Customer Segmentation*, *Churn Intelligence*, *Product Recommendations*, *Anomaly Detection*.
   - Click **Download Evaluation CSV** -> Verify `milestone4_test_results.csv` downloads cleanly.
   - Click **Re-Run All Evaluations** -> Confirm benchmark refreshes without error.
4. **Customer Segmentation:**
   - View 4 active segments: VIP/Loyal, Regular, Occasional, At-Risk.
   - Note header tag: `Silhouette Score: 0.3215`.
5. **Sales Forecasting:**
   - Switch to **Multi-Model Regressor Competition** tab.
   - Observe Prophet, Random Forest, and XGBoost with MAE, RMSE, and $R^2$ Score column (`N/A (1 test sample)`).
   - Click **Export Excel Business Report** -> Verify 6-sheet spreadsheet downloads.
6. **Product Recommendations:**
   - Select customer `C001` -> View hybrid recommendation suggestions and method attribution.
7. **Customer Churn Intelligence:**
   - Inspect churn cohort distribution and high-risk vs low-risk probabilities.
8. **Transaction Anomaly Detection:**
   - View flagged anomaly alerts with human review advisories.
9. **RBAC & Security Verification:**
   - Log out and log in as `exec` (Sales Executive).
   - Verify sales table is accessible, but executive dashboard blocks unauthorized AI modules with 403 Forbidden.
   - Log out and log in as `admin` -> Click **Test RBAC Guard Enforcement** -> Confirm green pass banner.
