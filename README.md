# MarketMind AI

### AI-Powered Small Business Sales Forecasting & Revenue Growth Intelligence Platform

> **Milestones 1–3 — Foundation, Customer & Sales Intelligence, Growth & Risk Intelligence**

---

## Project Overview

MarketMind AI helps small business owners understand their sales data, monitor inventory health, and grow revenue — without needing a data science team. The platform provides role-aware dashboards, real-time KPI monitoring, customer segmentation, sales forecasting, product recommendations, churn prediction, and anomaly detection.

### Problem Statement

Small businesses generate large amounts of sales and transaction data but lack the tools to turn it into actionable intelligence. Spreadsheets are slow, generic BI tools are expensive, and hiring analysts isn't feasible. MarketMind AI solves this with an intelligent, role-aware platform that surfaces the right insights to the right people.

### Target Users

| Role                | What they need                                                 |
| ------------------- | -------------------------------------------------------------- |
| **Owner / Admin**   | Full sales overview, transaction history, segments, forecasts  |
| **Store Manager**   | Inventory health, low-stock alerts, customer segments          |
| **Sales Executive** | Their own customer transactions (scoped to assigned customers) |

---

## Progress by Milestone

### Milestone 1 — Foundation & Core Infrastructure ✅

- [x] User authentication with JWT
- [x] Role-based access control (owner, admin, store_manager, sales_exec)
- [x] PostgreSQL database schema with SQLAlchemy ORM
- [x] REST API with FastAPI (sales transactions, inventory summary, transactions)
- [x] Data ingestion pipeline for two real datasets
- [x] Role-aware React frontend with live API integration
- [x] KPI dashboard (total units sold, total inventory, low-stock count)
- [x] Inventory management view (store manager role)
- [x] Sales transactions view (owner / admin role)

### Milestone 2 — Segmentation & Forecasting ✅

- [x] Customer segmentation with K-Means and Hierarchical Clustering, mapped to named business segments
- [x] Sales forecasting with Prophet, Random Forest and XGBoost, compared on a held-out period using MAE and RMSE
- [x] Business report generation (multi-sheet Excel)
- [x] `/segments` and `/forecast/revenue` endpoints with role protection
- [x] Dashboard panels for customer segments and the 30-day revenue forecast
- [x] Sales Executive view of their own customer transactions

### Milestone 3 — Recommendations, Churn & Anomaly Detection ✅

- [x] Product recommendations: Collaborative Filtering + Association Rule Mining (Apriori), combined into one output
- [x] Churn prediction: Logistic Regression, Random Forest and XGBoost compared on Precision / Recall / F1 / ROC-AUC (held-out split + 5-fold cross-validation), with High / Medium / Low retention-risk categories
- [x] Anomaly detection scripts: Z-score and Isolation Forest, with severity-rated alerts
- [x] `/recommendations`, `/churn` and `/anomalies` endpoints with role protection, plus dashboard panels (`M3Panels.jsx`) for recommendations, churn risk and anomaly alerts

---

## Tech Stack

| Layer        | Technology                                                 |
| ------------ | ---------------------------------------------------------- |
| **Backend**  | Python 3.11+, FastAPI, SQLAlchemy, PostgreSQL              |
| **Auth**     | JWT (python-jose), bcrypt (passlib)                        |
| **Frontend** | React 19, Vite 5                                           |
| **Data**     | Pandas (ETL pipeline)                                      |
| **ML**       | scikit-learn, XGBoost, Prophet, mlxtend, SciPy, Matplotlib |
| **Reports**  | openpyxl (Excel export)                                    |

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
│   │   ├── App.jsx       # Main app — login, dashboard, role-aware views, M2 AI panels
│   │   ├── M3Panels.jsx  # M3 panels — recommendations, churn risk, anomaly alerts
│   │   ├── App.css       # Styles
│   │   ├── main.jsx      # React entry point
│   │   └── index.css     # Global CSS reset
│   ├── index.html
│   ├── vite.config.js
│   └── package.json
├── ml/
│   ├── segmentation.py              # M2: K-Means + Hierarchical clustering -> segment_assignments.csv
│   ├── forecasting_prophet.py       # M2: Prophet baseline forecast
│   ├── forecasting_models.py        # M2: Random Forest + XGBoost vs Prophet (MAE / RMSE)
│   ├── generate_reports.py          # M2: segment summary, 30-day forecast, Excel report -> outputs/
│   ├── recommendations.py           # M3: Collaborative Filtering
│   ├── recommendations_complete.py  # M3: Association Rule Mining -> outputs/association_rules.csv
│   ├── recommendations_combined.py  # M3: combined "for you" + "frequently bought with" output
│   ├── churn_setup.py               # M3: churn label, features, Logistic Regression baseline
│   ├── churn_models.py              # M3: RF + XGBoost, risk categories -> outputs/churn_predictions.csv
│   ├── anomaly_detection.py         # M3: Z-score + Isolation Forest -> outputs/anomaly_alerts.csv
│   └── outputs/                     # Generated: JSON/CSV served by the API (segments, forecast, rules, churn, anomalies), Excel report
├── datasets/
│   ├── data_cleaning.py               # M1 cleaning/validation — reads raw/, writes processed/
│   ├── data_cleaning_segmentation.py  # M2 cleaning for the Online Retail dataset
│   ├── raw/
│   │   ├── sales_data_final.csv
│   │   ├── retail_sales_dataset_final.csv
│   │   └── OnlineRetail.csv
│   └── processed/
│       ├── sales_data_prepped.csv         # operations data (forecasting, anomaly detection)
│       ├── retail_sales_data_prepped.csv  # loaded by backend/load_data.py
│       ├── online_retail_prepped.csv      # customer-level data (segmentation, recommendations, churn)
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

### Running the ML Pipeline

All ML scripts run from inside `ml/` and read from `../datasets/processed/`. Run them in this order the first time (later scripts depend on earlier outputs):

```bash
# 1. Prepare the Online Retail data (once)
cd datasets && python data_cleaning_segmentation.py && cd ..

cd ml

# 2. Milestone 2
python segmentation.py          # writes segment_assignments.csv
python forecasting_prophet.py
python forecasting_models.py
python generate_reports.py      # writes outputs/*.json and outputs/business_report.xlsx

# 3. Milestone 3
python recommendations.py
python recommendations_complete.py   # writes outputs/association_rules.csv (needed by the API)
python recommendations_combined.py    # demo of the combined output
python churn_setup.py
python churn_models.py               # writes outputs/churn_predictions.csv (needs segment_assignments.csv)
python anomaly_detection.py          # writes outputs/anomaly_alerts.csv
```

The AI endpoints read the files in `ml/outputs/`: `/segments` and `/forecast/revenue` read JSON from `generate_reports.py`; `/churn` and `/anomalies` read `churn_predictions.csv` and `anomaly_alerts.csv`; `/recommendations` loads `association_rules.csv` plus the customer purchase history. Re-run the relevant script to refresh a result — no server restart needed (the recommendation engine is built on the first request after server start, which takes a few seconds).

> Generated CSVs in `ml/outputs/` are not all committed to git, so on a fresh clone run the pipeline above once before using the dashboard panels.

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

| Method | Path                  | Auth                        | Description                                                                                                                                               |
| ------ | --------------------- | --------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `POST` | `/register`           | Public                      | Create a new user                                                                                                                                         |
| `POST` | `/login`              | Public                      | Returns JWT access token                                                                                                                                  |
| `GET`  | `/me`                 | Any logged-in user          | Current user profile + role                                                                                                                               |
| `GET`  | `/sales-transactions` | owner, store_manager, admin | Sales transaction list (limit 50)                                                                                                                         |
| `GET`  | `/transactions`       | owner, admin, sales_exec    | Transaction list (sales_exec sees only their customers)                                                                                                   |
| `GET`  | `/sales/summary`      | owner, store_manager, admin | KPI totals: units sold, inventory, low-stock count                                                                                                        |
| `GET`  | `/segments`           | owner, store_manager, admin | Customer count and average purchase value per segment                                                                                                     |
| `GET`  | `/forecast/revenue`   | owner, admin                | Predicted revenue for the next 30 days (XGBoost)                                                                                                          |
| `GET`  | `/recommendations`    | owner, admin, store_manager | `?customer_id=17850&current_product=<exact name>` — personalised "recommended for you" + "frequently bought with" (404 if the customer has no history)    |
| `GET`  | `/churn`              | owner, admin                | Churn probability + risk category per customer; `?risk=High Risk` and `?limit=` (default 100, max 500). Includes `risk_summary` counts over all customers |
| `GET`  | `/anomalies`          | owner, admin, store_manager | Fraud / inventory alerts, high severity first; `?severity=high\|medium` and `?limit=`                                                                     |
| `GET`  | `/admin-only`         | admin                       | Admin-only test route                                                                                                                                     |

`/segments` and `/forecast/revenue` return `404` until `ml/generate_reports.py` has been run; `/churn` and `/anomalies` return `404` until `churn_models.py` / `anomaly_detection.py` have been run; `/recommendations` returns `404` until `recommendations_complete.py` has been run.

---

## Data

Raw source files live in `datasets/raw/` and are committed to the repository alongside the cleaned output, so the full pipeline is reproducible end-to-end without needing external files.

| Dataset                          | Used for                                                            |
| -------------------------------- | ------------------------------------------------------------------- |
| `sales_data_final.csv`           | Inventory KPIs, demand forecasting, anomaly detection (76,000 rows) |
| `retail_sales_dataset_final.csv` | Original customer transactions loaded into PostgreSQL               |
| `OnlineRetail.csv`               | Customer segmentation, recommendations, churn (4,338 customers)     |

To regenerate the prepped data from the raw files:

```bash
cd datasets
python data_cleaning.py                # sales_data + retail_sales_dataset -> processed/
python data_cleaning_segmentation.py   # OnlineRetail -> online_retail_prepped.csv
```

`data_cleaning.py` runs the Day 5-6 checks (nulls, duplicates, range sanity checks — see the script for the full exploration) and writes two cleaned CSVs plus a product lookup into `datasets/processed/`:

| File                                               | Contents                                                                                     |
| -------------------------------------------------- | -------------------------------------------------------------------------------------------- |
| `datasets/processed/sales_data_prepped.csv`        | Store ID, Product ID, Date, Units Sold, Inventory Level, Demand, Price and related fields    |
| `datasets/processed/retail_sales_data_prepped.csv` | Customer ID, Gender, Age, Date, Product Category, Quantity, Price per Unit, Total Amount     |
| `datasets/processed/online_retail_prepped.csv`     | InvoiceNo, StockCode, Description, Quantity, InvoiceDate, UnitPrice, CustomerID, TotalAmount |
| `datasets/processed/product_lookup.csv`            | Product ID -> Category, one row per product (see note below)                                 |

**On `product_lookup.csv` specifically:** the raw `sales_data_final.csv` has a real data quality issue — the same Product ID shows up with 2-3 _different_ categories across rows (confirmed for all 20 products, a synthetic-data generation artifact, not a few stray typos). Since the `Product` table's primary key is `product_id`, only one category per product can be stored. Resolved by taking the **most frequent category per Product ID** (mode) rather than an arbitrary first-seen value — see the "2.5" section of `data_cleaning.py` for the exact logic and reasoning.

`backend/load_data.py` reads the prepped files from `../datasets/processed/`. Just run it from inside `backend/` as shown above.

---

## AI Modules

### Customer Segmentation (M2)

K-Means and Hierarchical Clustering on purchase frequency, purchase value and recency. Customers are assigned to four named segments: **Regular Shoppers**, **Lapsed / One-Time Buyers**, **High-Value Customers** and **Power Buyers**. Output: `segment_assignments.csv` (written to the folder the script is run from, i.e. `ml/`; scripts also find it in `ml/outputs/`).

### Sales Forecasting (M2)

Daily demand forecast with Prophet, Random Forest and XGBoost, compared on a held-out final 90 days using MAE and RMSE. The dashboard forecast sums a recursive 30-day XGBoost revenue forecast (each predicted day feeds the next day's lag features).

### Product Recommendations (M3)

Two techniques combined: **Collaborative Filtering** (cosine similarity between customers) for personalised "recommended for you" suggestions, and **Association Rule Mining** (Apriori, min support 2%, min confidence 30%, lift > 1) for "frequently bought with" cross-sell suggestions. Product names are whitespace-normalised so the same product is never counted twice. Rules are saved to `ml/outputs/association_rules.csv` (multi-item sets are joined with `||` because product names can contain commas); the API returns individual products ranked by lift, and falls back to popular items when a customer has too few similar neighbours.

### Churn Prediction (M3)

A customer is labelled churned if they make no purchase in the 90 days after a cutoff date; features (order frequency, days since last purchase, average order value) are built only from activity before the cutoff, so the model predicts the future from the past with no label leakage. Logistic Regression, Random Forest and XGBoost are compared on Precision, Recall, F1 and ROC-AUC, both on a held-out 20% split and with 5-fold cross-validation. The winner is chosen on cross-validated F1; when models are within 0.02 F1 (they are statistically tied on this data) the higher-Recall model is preferred, since missing an at-risk customer costs more than a wasted offer. On the Online Retail data the churn rate is ~43% and ROC-AUC is ~0.73 — churn is only moderately predictable from order history, so treat probabilities as a ranking for retention outreach, not as certainties (the 13% / XGBoost figures in the learning handout are illustrative). The selected model scores every customer as High / Medium / Low risk (thresholds 0.7 / 0.4). Output: `ml/outputs/churn_predictions.csv` (the model used is recorded in the `model_used` column).

### Anomaly Detection (M3)

Two complementary methods on the operations data: a **Z-score** check on revenue (single feature) and an **Isolation Forest** across units sold, inventory, orders, price, revenue and sell-through (multiple features). Flagged rows become alerts with a `high` / `medium` severity (`high` when both methods agree or revenue exceeds 5x the average). Alerts keep their `z_score` and `iso_score` and are ranked high-severity-first, most anomalous first, so the dashboard's top 100 are the most suspicious. Outputs: `ml/outputs/anomaly_alerts.csv` and `ml/outputs/anomaly_comparison.csv` (every flagged row with both methods' scores).

---

## Role-Based Dashboard

After login the frontend detects the user's role from `/me` and renders the appropriate view:

**Owner / Admin** — KPI cards, customer segments panel, 30-day sales forecast panel, and the full sales transactions table.

**Store Manager** — KPI cards, customer segments panel, and an inventory overview sorted by stock level (ascending) with a "Reorder soon" flag for items below 100 units.

**Sales Executive** — A table of their own customer transactions (invoice, customer, item, quantity, total), scoped to their assigned customers.

**M3 panels** (`M3Panels.jsx`): _Product Recommendations_ (owner, admin, store manager — enter a customer ID and optionally an exact product name), _Customer Churn Risk_ (owner, admin — risk counts plus the 100 highest-risk customers), and _Anomaly Alerts_ (owner, admin, store manager). Sales executives see none of them, since the API denies them access.

The segments and forecast panels render only when the API returns data, so roles without access simply don't see them.

---

## Roadmap

| Milestone     | Focus                                                                                             |
| ------------- | ------------------------------------------------------------------------------------------------- |
| **M1** ✅     | Foundation: auth, RBAC, data ingestion, live API, role-aware dashboard                            |
| **M2** ✅     | Customer segmentation, sales forecasting, reports, dashboard integration                          |
| **M3** ✅     | Recommendations, churn prediction, anomaly detection — models, API endpoints and dashboard panels |
| **M4 (next)** | Testing, UI polish, Docker and cloud deployment                                                   |

---

## Known Limitations (to address in M4)

- `POST /register` is public and accepts any `role_id`, so anyone can create an owner/admin account. Restrict it to admins (or remove it after seeding) before deployment.
- Frontend API URLs are hard-coded to `http://127.0.0.1:8000` and CORS allows only the local Vite origins — move both to environment variables for deployment.
- The anomaly and churn results are batch outputs; re-run the scripts to refresh them. The anomaly dataset is synthetic, so a large share of rows are flagged as "99% of stock sold" — tune `Z_THRESHOLD` / `CONTAMINATION` in `anomaly_detection.py` for real data.
- No automated tests yet.

---

## Contributing

This project is developed as part of the Infosys Springboard Virtual Internship Program 2026.

---

## License

MIT
