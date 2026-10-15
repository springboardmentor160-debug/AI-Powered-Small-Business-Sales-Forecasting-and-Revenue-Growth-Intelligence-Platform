<div align="center">

# MarketMind AI

**Sales intelligence for small businesses: forecasting, customer segmentation, recommendations, churn prediction and anomaly detection in one role-aware dashboard.**

</div>

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Quick Start (Docker)](#quick-start-docker)
- [Local Development](#local-development)
- [Machine Learning Pipeline](#machine-learning-pipeline)
- [Model Performance](#model-performance)
- [API Reference](#api-reference)
- [Access Control](#access-control)
- [Configuration](#configuration)
- [Project Structure](#project-structure)
- [Testing](#testing)
- [Deployment](#deployment)
- [Security](#security)
- [Known Limitations](#known-limitations)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgements](#acknowledgements)

---

## Overview

Small retailers collect a lot of sales and customer data but rarely have analysts to make sense of it. Spreadsheets are slow, general-purpose BI tools are costly, and a data science team is out of reach.

**MarketMind AI** is a full-stack platform that turns transaction and inventory data into decisions:

- **What will we sell?** A 30-day revenue forecast.
- **Who are our customers?** Four behavioural segments, from Power Buyers to Lapsed customers.
- **What should we offer them?** Personalised recommendations and "frequently bought together" suggestions.
- **Who is about to leave?** A churn-risk score for every customer.
- **What looks wrong?** Alerts for unusual sales and inventory activity.

Each person sees only what their job needs: owners get the full picture, store managers get inventory and alerts, and sales executives see only their own customers. The whole platform runs from a single `docker compose up`.

## Features

### Platform

- **Authentication:** stateless JWT login with bcrypt password hashing.
- **Role-based access control:** four roles (`owner`, `admin`, `store_manager`, `sales_exec`) enforced on the server for every endpoint, with data scoping for sales executives.
- **Role-aware dashboard:** the React interface adapts to the signed-in role, hides what a role cannot use and never shows a false error for it.
- **Resilient by design:** request timeouts, loading states, per-panel failure handling, session-expiry handling, and clear `4xx`/`503` API responses instead of stack traces.
- **Excel business report:** downloadable multi-sheet workbook (segments, forecast summary, daily forecast).
- **One-command deployment:** Docker Compose stack (PostgreSQL, API, nginx) with a safe, idempotent first-start data loader, plus a Render blueprint.

### AI modules

| Module                      | What it does                                                                                            | Method                                                                                         |
| --------------------------- | ------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| **Customer segmentation**   | Groups customers into Regular Shoppers, Lapsed / One-Time Buyers, High-Value Customers and Power Buyers | RFM features, K-Means and Hierarchical Clustering                                              |
| **Sales forecasting**       | Forecasts demand and a 30-day revenue figure                                                            | Prophet, Random Forest and XGBoost compared on a held-out period; recursive multi-day forecast |
| **Product recommendations** | "Recommended for you" and "Frequently bought together"                                                  | Collaborative filtering (cosine similarity) and association rules (Apriori)                    |
| **Churn prediction**        | Probability and High / Medium / Low risk tier per customer                                              | Logistic Regression, Random Forest and XGBoost; leakage-free time-based labelling              |
| **Anomaly detection**       | Severity-rated alerts for unusual sales and inventory rows                                              | Z-score on revenue and a multivariate Isolation Forest                                         |

## Architecture

```text
                       ┌───────────────────── Docker Compose ─────────────────────┐
                       │                                                          │
  Browser ──► nginx :8080 ──┬── /      React app (static build)                   │
                       │    │                                                     │
                       │    └── /api ──► FastAPI + uvicorn :8000 ──► PostgreSQL   │
                       │                       │                                  │
                       │                       ├─ reads ml/outputs/   (forecast, segments, churn,
                       │                       │                       anomalies, association rules)
                       │                       └─ reads datasets/processed/  (live recommendations)
                       └──────────────────────────────────────────────────────────┘

  Offline:  ml/*.py  ── train / score ──►  ml/outputs/   (CSV and JSON the API serves)
```

**Design decisions**

- **Models run offline, the API serves their results.** Training and scoring happen in `ml/` scripts and write files to `ml/outputs/`. The API reads those files, so requests are fast and no heavy library runs per request. Re-run a script to refresh a result; no restart is needed.
- **Recommendations are computed live.** A sparse customer-by-product matrix (about 3 MB) is built once at startup in roughly two seconds, then each lookup takes milliseconds.
- **Single origin.** nginx serves the app and proxies `/api`, so the browser never makes a cross-origin request.
- **Authorisation lives on the server.** Hiding a panel in the browser is only a convenience; every endpoint checks the caller's role.

## Tech Stack

| Layer       | Technologies                                                  |
| ----------- | ------------------------------------------------------------- |
| Backend     | Python 3.11, FastAPI, Uvicorn, Pydantic v2, SQLAlchemy 2      |
| Database    | PostgreSQL 16                                                 |
| Security    | python-jose (JWT), passlib with bcrypt                        |
| Frontend    | React 19, Vite 5, plain CSS (grid and flexbox)                |
| Data and ML | pandas, NumPy, SciPy, scikit-learn, XGBoost, Prophet, mlxtend |
| Reporting   | openpyxl                                                      |
| Delivery    | Docker, Docker Compose, nginx                                 |

## Quick Start (Docker)

**Prerequisites:** Docker with the Compose plugin.

```bash
git clone <your-repository-url> marketmindAI
cd marketmindAI

cp .env.example .env
# edit .env: set POSTGRES_PASSWORD, SECRET_KEY and DEMO_PASSWORD

docker compose up --build -d
docker compose logs -f backend      # wait for "[bootstrap] ready"
```

Open **http://localhost:8080**. Interactive API docs are at **http://localhost:8080/api/docs**.

The first start creates the tables and loads about 470,000 rows (roughly a minute). Later starts take seconds and keep your data in the `pgdata` volume.

With `SEED_DEMO_USERS=true` in `.env`, these accounts exist (password = your `DEMO_PASSWORD`):

| Role            | Email                                     |
| --------------- | ----------------------------------------- |
| Owner           | `owner@test.com`                          |
| Admin           | `admin@test.com`                          |
| Store manager   | `manager@test.com`                        |
| Sales executive | `sales@test.com` (assigned 200 customers) |

```bash
docker compose ps          # service status and health
docker compose down        # stop (data is kept)
docker compose down -v     # stop and delete the database
```

See [DEPLOYMENT.md](DEPLOYMENT.md) for servers, Render, environment variables and troubleshooting.

## Local Development

**Prerequisites:** Python 3.11+, Node.js 18+, a running PostgreSQL instance.

### 1. Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate              # Windows: venv\Scripts\activate
pip install -r ../requirements.txt

cp .env.example .env                  # set DATABASE_URL and SECRET_KEY
python bootstrap.py                   # create tables, seed roles, load data (safe to re-run)
uvicorn main:app --reload             # http://localhost:8000  (docs at /docs)
```

`bootstrap.py` is the recommended setup: it never drops data and bulk-loads quickly. To also create demo logins, set `SEED_DEMO_USERS=true` and `DEMO_PASSWORD` in `.env` first. The older `init_db.py` (drops and recreates all tables) and `load_data.py` (row-by-row inserts, slow) still work if you prefer them.

### 2. Frontend

```bash
cd frontend
npm install
npm run dev                           # http://localhost:5173
```

The app calls `http://127.0.0.1:8000` by default; set `VITE_API_URL` to change it.

### 3. Create users manually (optional)

If you did not use demo users, register one account per role through `POST /register` (role ids: `1` owner, `2` admin, `3` sales_exec, `4` store_manager):

```json
{
  "name": "Platform Owner",
  "email": "owner@example.com",
  "password": "use-a-strong-password",
  "role_id": "1"
}
```

## Machine Learning Pipeline

The scripts read from `datasets/processed/` and write to `ml/outputs/`, which is committed so the API and the Docker image work without retraining. Run them from `ml/` in this order the first time:

```bash
# once: clean the retail data
cd datasets && python data_cleaning_segmentation.py && cd ../ml

python segmentation.py                # -> segment_assignments.csv
python forecasting_prophet.py
python forecasting_models.py
python generate_reports.py            # -> segment_summary.json, forecast_summary.json, business_report.xlsx
python recommendations.py
python recommendations_complete.py    # -> association_rules.csv
python recommendations_combined.py
python churn_setup.py
python churn_models.py                # -> churn_predictions.csv
python anomaly_detection.py           # -> anomaly_alerts.csv
python milestone4_testing.py          # -> milestone4_test_results.csv
```

| Endpoint                                              | Reads                                                             |
| ----------------------------------------------------- | ----------------------------------------------------------------- |
| `/segments`, `/forecast/revenue`, `/reports/business` | output of `generate_reports.py`                                   |
| `/churn`                                              | `churn_predictions.csv`                                           |
| `/anomalies`                                          | `anomaly_alerts.csv`                                              |
| `/recommendations` ("frequently bought with")         | `association_rules.csv`                                           |
| `/recommendations` ("recommended for you")            | computed live from `datasets/processed/online_retail_prepped.csv` |

### How each model is built

**Segmentation.** Recency, frequency and average purchase value are scaled and clustered with K-Means and Hierarchical Clustering. Extreme bulk buyers are excluded first so they do not distort the groups, and each cluster is mapped to a named segment.

**Forecasting.** Tree models cannot see time, so they receive engineered features: day of week, month, day of year, demand 1 and 7 days earlier, and a 7-day rolling mean (shifted so a day never leaks into its own feature). The last 90 days are held out, with a chronological split. The dashboard figure sums a recursive 30-day forecast in which each predicted day feeds the next day's lag features.

**Recommendations.** Collaborative filtering recommends products bought by the five most similar customers that the customer has not bought. Association rules come from Apriori with minimum support 2% and confidence 30%, ranked by lift.

**Churn.** A customer is churned if they make no purchase in the 90 days after a cutoff date. Features (order frequency, days since last purchase, average order value) use only activity before the cutoff, so the model predicts the future from the past with no label leakage. The best model by F1 on a stratified held-out set scores every customer; risk tiers use probability thresholds of 0.7 (High) and 0.4 (Medium).

**Anomaly detection.** A Z-score test (threshold 3) flags extreme revenue, and an Isolation Forest (contamination 2%) looks at units sold, inventory, units ordered, price, revenue and sell-through together. An alert is `high` when both methods agree or revenue exceeds five times the average, otherwise `medium`.

## Model Performance

Measured by `ml/milestone4_testing.py` on the project's datasets.

| Module                                     | Metric                               | Result                    |
| ------------------------------------------ | ------------------------------------ | ------------------------- |
| Forecasting: Random Forest (1-day-ahead)   | MAE / RMSE / R²                      | 752 / 1,008 / 0.59        |
| Forecasting: XGBoost (1-day-ahead)         | MAE / RMSE / R²                      | 960 / 1,476 / 0.11        |
| Forecasting: XGBoost (90-day recursive)    | R²                                   | -0.45                     |
| Segmentation: K-Means (k=4)                | Silhouette                           | 0.544                     |
| Segmentation: Hierarchical (k=4)           | Silhouette                           | 0.519                     |
| Churn: Logistic Regression (best)          | Accuracy / Precision / Recall / F1   | 0.66 / 0.60 / 0.61 / 0.61 |
| Churn: XGBoost                             | F1                                   | 0.58                      |
| Churn: Random Forest                       | F1                                   | 0.54                      |
| Recommendations: collaborative filtering   | Precision@3 / Recall@3               | 0.045 / 0.007             |
| Recommendations: popularity baseline       | Precision@3 / Recall@3               | 0.049 / 0.005             |
| Anomaly detection (150 injected anomalies) | Detection rate / False-positive rate | 68% / 1.87%               |

These numbers are reported as measured, including the unflattering ones. See [Known Limitations](#known-limitations) for what they imply.

## API Reference

Interactive documentation is served at `/docs` (`/api/docs` behind nginx). Protected routes need `Authorization: Bearer <token>` from `POST /login`.

| Method | Endpoint                                                 | Roles                       | Description                                                                          |
| ------ | -------------------------------------------------------- | --------------------------- | ------------------------------------------------------------------------------------ |
| `GET`  | `/health`                                                | Public                      | Liveness and database check                                                          |
| `POST` | `/register`                                              | Public                      | Create a user (rejects duplicate emails and unknown roles)                           |
| `POST` | `/login`                                                 | Public                      | Returns a signed JWT access token                                                    |
| `GET`  | `/me`                                                    | Any signed-in user          | Current user and role                                                                |
| `GET`  | `/sales/summary`                                         | owner, admin, store_manager | Total units sold, total inventory, low-stock count                                   |
| `GET`  | `/sales-transactions`                                    | owner, admin, store_manager | Sales ledger (first 50 rows)                                                         |
| `GET`  | `/transactions`                                          | owner, admin, sales_exec    | Customer transactions (first 50; sales executives see only their assigned customers) |
| `GET`  | `/segments`                                              | owner, admin, store_manager | Customer count and average value per segment                                         |
| `GET`  | `/forecast/revenue`                                      | owner, admin                | Predicted revenue for the next 30 days                                               |
| `GET`  | `/reports/business`                                      | owner, admin                | Download the Excel business report                                                   |
| `GET`  | `/recommendations?customer_id=17850&current_product=...` | owner, admin, store_manager | Personalised picks, plus "frequently bought with" when `current_product` is given    |
| `GET`  | `/churn`                                                 | owner, admin                | Risk counts for all customers and the 100 highest-risk customers                     |
| `GET`  | `/anomalies`                                             | owner, admin, store_manager | High and medium alert counts and the 100 highest-priority alerts                     |
| `GET`  | `/admin-only`                                            | admin                       | Role-check test route                                                                |

**Error responses** use a consistent `{"detail": "..."}` body: `400` invalid input, `401` missing or expired token, `403` role not allowed, `404` unknown customer, `422` malformed parameter, `503` data or database temporarily unavailable.

## Access Control

| Capability                        | Owner | Admin | Store manager |       Sales exec        |
| --------------------------------- | :---: | :---: | :-----------: | :---------------------: |
| KPI summary and sales ledger      |  ✅   |  ✅   |      ✅       |           ❌            |
| Customer transactions             |  ✅   |  ✅   |      ❌       | ✅ (own customers only) |
| Customer segments                 |  ✅   |  ✅   |      ✅       |           ❌            |
| Recommendations                   |  ✅   |  ✅   |      ✅       |           ❌            |
| Anomaly alerts                    |  ✅   |  ✅   |      ✅       |           ❌            |
| Churn risk                        |  ✅   |  ✅   |      ❌       |           ❌            |
| Revenue forecast and Excel report |  ✅   |  ✅   |      ❌       |           ❌            |

## Configuration

| Variable            | Used by               | Description                                                                                                        | Default                                       |
| ------------------- | --------------------- | ------------------------------------------------------------------------------------------------------------------ | --------------------------------------------- |
| `DATABASE_URL`      | backend               | PostgreSQL connection string (`postgres://` is accepted)                                                           | none (required)                               |
| `SECRET_KEY`        | backend               | Signs JWTs; use a long random value                                                                                | none (required)                               |
| `CORS_ORIGINS`      | backend               | Comma-separated frontend origins; only needed when the frontend is on another domain                               | `http://localhost:5173,http://127.0.0.1:5173` |
| `SEED_DEMO_USERS`   | backend               | Create the demo accounts (`owner@test.com`, `admin@test.com`, `sales@test.com`, `manager@test.com`) on first start | `false`                                       |
| `DEMO_PASSWORD`     | backend               | Password for the demo accounts                                                                                     | none                                          |
| `PORT`              | backend               | Port to listen on                                                                                                  | `8000`                                        |
| `ROOT_PATH`         | backend               | URL prefix when behind a proxy (`/api` in Compose)                                                                 | none                                          |
| `VITE_API_URL`      | frontend (build time) | API base URL baked into the app                                                                                    | `http://127.0.0.1:8000`                       |
| `POSTGRES_PASSWORD` | Compose               | Database password (letters and digits only)                                                                        | none (required)                               |
| `APP_PORT`          | Compose               | Published port                                                                                                     | `8080`                                        |

Generate a secret key with `python -c "import secrets; print(secrets.token_hex(32))"`.

## Project Structure

```text
marketmindAI/
├── backend/
│   ├── main.py                    # FastAPI app: routes, RBAC, error handling
│   ├── models.py                  # SQLAlchemy models
│   ├── schemas.py                 # Pydantic schemas
│   ├── auth.py                    # Password hashing and JWT helpers
│   ├── database.py                # Engine and connection settings
│   ├── bootstrap.py               # First start: create tables, seed roles, bulk-load data
│   ├── init_db.py                 # Local dev: recreate all tables (destructive)
│   ├── load_data.py               # Local dev: row-by-row data loader
│   ├── requirements-prod.txt      # Slim runtime dependencies for the container
│   ├── Dockerfile
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── App.jsx                # Login, role-aware dashboard, AI panels
│   │   ├── M3Panels.jsx           # Recommendations, churn risk and anomaly panels
│   │   ├── App.css
│   │   ├── main.jsx
│   │   └── index.css
│   ├── Dockerfile                 # Build the app, serve it with nginx
│   ├── nginx.conf                 # Static files and the /api proxy
│   ├── index.html
│   ├── vite.config.js
│   └── package.json
├── ml/
│   ├── segmentation.py
│   ├── forecasting_prophet.py
│   ├── forecasting_models.py
│   ├── generate_reports.py
│   ├── recommendations.py
│   ├── recommendations_complete.py
│   ├── recommendations_combined.py
│   ├── churn_setup.py
│   ├── churn_models.py
│   ├── anomaly_detection.py
│   ├── milestone4_testing.py
│   └── outputs/                   # Results served by the API (committed)
├── datasets/
│   ├── data_cleaning.py
│   ├── data_cleaning_segmentation.py
│   ├── raw/                       # Source files
│   └── processed/                 # Cleaned files used by the loaders and ML scripts
├── docker-compose.yml
├── .env.example                   # Secrets template for Compose
├── .dockerignore
├── render.yaml                    # Render blueprint
├── DEPLOYMENT.md
├── requirements.txt               # Full development and training dependencies
├── LICENSE
└── README.md
```

## Testing

**Model evaluation.** `python ml/milestone4_testing.py` re-runs every metric in [Model Performance](#model-performance) and writes `ml/outputs/milestone4_test_results.csv`.

| Module            | How it is tested                                                                                                                                                      |
| ----------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Forecasting       | MAE, RMSE and R² on a chronological 90-day holdout, plus a 90-day recursive run and a train-versus-test R² overfitting check                                          |
| Segmentation      | Silhouette score for both algorithms and for k = 2 to 6                                                                                                               |
| Churn             | Accuracy, precision, recall and F1 on a stratified test set, for all three models                                                                                     |
| Recommendations   | Precision@K and Recall@K on a time-based holdout (recommend from history before a cutoff, count only products first bought afterwards), against a popularity baseline |
| Anomaly detection | Detection rate, precision and false-positive rate on 150 injected anomalies of three kinds                                                                            |

**Behaviour checks.** The error and permission paths were exercised against the running API: wrong credentials, duplicate registration, missing or corrupted result files, an unavailable database, forbidden roles, unknown customers and malformed parameters. A manual end-to-end checklist is in `milestone4_integration_checklist.md`.

## Deployment

The `docker-compose.yml` stack is production-shaped (health checks, non-root API container, database on an internal network, secrets from the environment). [DEPLOYMENT.md](DEPLOYMENT.md) covers running on a server behind HTTPS, deploying to Render with `render.yaml`, refreshing ML results without a rebuild, and troubleshooting.

## Security

- Passwords are hashed with bcrypt; tokens are signed JWTs.
- Authorisation is enforced server-side on every protected route, and sales executives are scoped to their assigned customers.
- Login failures return one message for unknown email and wrong password, so accounts cannot be enumerated.
- Secrets come from environment variables; `.env` files are git-ignored and excluded from Docker images.
- CORS is limited to configured origins, and the database is not published outside the Compose network.
- Before sharing a deployment: use unique `SECRET_KEY` and `POSTGRES_PASSWORD` values, set `SEED_DEMO_USERS=false` (or use a strong `DEMO_PASSWORD`), and serve over HTTPS.

## Known Limitations

- **The sales forecast is indicative, not reliable.** XGBoost scores R² 1.00 on training data but 0.11 on held-out data, and a true multi-day forecast scores below the average. Random Forest generalises better and is the first thing to switch to.
- **Collaborative filtering does not beat a popularity baseline** on this dataset. The association rules are the more useful half of the recommender.
- **Churn is hard to predict from three behavioural features.** The simplest model (Logistic Regression) wins; more complex models did not earn their complexity.
- **The anomaly detector misses single-signal problems** such as stock vanishing (4% detected in testing) and flags about 2% of rows by design. A rule such as "units sold exceeds inventory" would cover the gap.
- **The operations dataset is synthetic**, which limits what the forecasting and anomaly modules can learn. Anomaly testing used injected cases, not confirmed fraud.
- **Results are batch-computed.** The API serves the output of offline scripts; numbers refresh only when the scripts are re-run.

## Roadmap

- [x] JWT authentication, role-based access control and PostgreSQL schema
- [x] Customer segmentation and sales forecasting with Excel reporting
- [x] Recommendations, churn prediction and anomaly detection, with dashboard panels
- [x] Formal model evaluation, error handling and UX polish
- [x] Docker packaging and deployment guide
- [ ] Switch the dashboard forecast to Random Forest and evaluate with rolling-origin cross-validation
- [ ] Rule-based inventory checks alongside the Isolation Forest
- [ ] Matrix-factorisation recommendations, benchmarked against the popularity baseline
- [ ] Scheduled background jobs so model results refresh automatically
- [ ] Continuous integration with automated tests, and HTTPS plus managed secrets in production

## Contributing

Contributions are welcome.

1. Fork the repository and create a branch: `git checkout -b feature/short-description`.
2. Make your change. Keep endpoints role-protected and error responses in the `{"detail": ...}` format.
3. If you change a model or its preprocessing, re-run `python ml/milestone4_testing.py` and include the new numbers in your pull request.
4. Run the backend and frontend locally (see [Local Development](#local-development)) and check the affected screens for each role.
5. Open a pull request describing what changed and why.

Please open an issue first for larger changes.

## License

Released under the [MIT License](LICENSE).

## Acknowledgements

- The retail transaction data is the [Online Retail dataset](https://archive.ics.uci.edu/dataset/352/online+retail) from the UCI Machine Learning Repository.
- The store and product operations data is synthetic.
- Built with [FastAPI](https://fastapi.tiangolo.com/), [React](https://react.dev/), [scikit-learn](https://scikit-learn.org/), [XGBoost](https://xgboost.ai/), [Prophet](https://facebook.github.io/prophet/) and [mlxtend](https://rasbt.github.io/mlxtend/).
