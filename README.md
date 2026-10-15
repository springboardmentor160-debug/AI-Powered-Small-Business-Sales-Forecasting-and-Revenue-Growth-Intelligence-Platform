# MarketMind AI
**Small Business Sales Intelligence Platform**

**Author:** Anubhav Kumar Gupta
**Project:** MarketMind AI internship project (Milestones 1–4)
**Run mode:** local development (not publicly deployed)

---

## 1. Overview

MarketMind AI turns retail sales and customer data into decisions a small business can act on. A React dashboard talks to a FastAPI backend with
login, role-based access and a SQLite database. Machine-learning scripts produce forecasts, customer segments, product recommendations,
churn risk and anomaly alerts, which the dashboard reads.

| What you can do | Where |
|---|---|
| See revenue, units, top product and low-stock alerts for the last 7 / 30 / 90 days, 12 months or all time | Dashboard |
| Track the sales trend with a 30-day forecast, and revenue by category, store and product | Dashboard |
| Group customers into segments and see churn risk per customer | Customers |
| Get "recommended for you" and "frequently bought with" suggestions | Customers |
| Check stock health, days of cover and suggested reorder quantities | Inventory |
| Review unusual sales / stock records | Anomalies |
| Create and track invoices | Invoices |
| See how well every model performed | Model reports |
| Manage users | Users (admin only) |
| Download an Excel business report | Export report |

## 2. Milestones

| Milestone | Focus | Status |
|---|---|---|
| M1 | Data cleaning, database, authentication, role-based access, sales analytics, invoices | Implemented |
| M2 | Customer segmentation (K-Means + hierarchical), revenue forecasting, Excel report | Implemented |
| M3 | Recommendations, churn prediction, anomaly detection, inventory intelligence | Implemented |
| M4 | Model evaluation, error handling, tests, UI polish, forgot-password, date-range filter, documentation | Implemented; see section 11 for what has been verified |

## 3. Architecture

```
React (Vite) dashboard
        │  HTTPS/JSON + JWT bearer token
        ▼
FastAPI backend ── auth + role checks (ACCESS matrix in backend/auth.py)
        │
        ├── SQLite database  (users, invoices, sales rows, catalogue)
        └── ml/outputs/      (JSON / CSV written by the ML scripts, served by the API)
                ▲
                │  pandas + scikit-learn pipeline
        datasets/raw  →  cleaning  →  datasets/processed
```

Store data is queried live from the database. AI results are pre-computed by the ML scripts and read from `ml/outputs/`.
Details: `docs/ARCHITECTURE.md`.

## 4. Technology

| Layer | Technology |
|---|---|
| Backend | Python 3.11, FastAPI, SQLAlchemy 2, SQLite |
| Auth | JWT (python-jose), bcrypt |
| Frontend | React 19, Vite 5 |
| Data | pandas |
| ML | scikit-learn, XGBoost, Prophet, mlxtend, SciPy, Matplotlib |
| Reports | openpyxl |

## 5. Data

| Dataset | Raw rows | After cleaning | Used for |
|---|---|---|---|
| Store / inventory data (5 stores × 20 products, 2022-01-01 to 2024-01-01) | 73,100 | 73,100 (0 missing, 0 duplicates) | forecasting, anomalies, inventory, sales analytics |
| UCI Online Retail II (2009-12 to 2011-12) | 1,067,371 | 776,854 lines, 5,853 customers | segmentation, recommendations, churn |

**Observed vs derived.** Quantities, prices and dates are observed in the source files. Revenue (`units × price × (1 − discount)`), order
counts, segments and risk scores are derived. The store file has no reorder level, so `reorder_point` is derived as one day of average sales
(minimum 10), and "days of cover" is stock divided by average daily units sold. These are estimates, not physical stock counts.

**Date handling.** The store data ends on 2024-01-01. By default the dashboard shows every date moved forward so the newest record is *today*,
and it says so on screen. Nothing in the database changes. Set `REBASE_DATES_TO_TODAY=0` in `backend/.env` to see the real dates.
The store data looks synthetic (no trend or weekly pattern), while Online Retail II is real.

## 6. Features in detail

**Authentication and roles.** Register, login, JWT tokens, bcrypt password hashing. Roles: `business_owner`, `store_manager`,
`sales_executive`, `admin`. Every request re-checks the user in the database, so deleted users lose access immediately.

**Forgot password.** The login page sends a one-time reset link by e-mail (valid 30 minutes, usable once, one e-mail per minute per account).
Only a hash of the token is stored, and the page answers the same way whether or not the address exists. Without SMTP settings the link is
printed in the backend terminal and saved in `data/outbox/`.

**Administrator sign-up.** "Administrator" is available when creating an account, but needs the access code set in `ADMIN_REGISTRATION_CODE`.
While that value is empty, admin sign-up is switched off.

**Date range.** A dropdown (7 days / 30 days / 90 days / 12 months / all time) filters the KPI cards (with % change versus the previous
period), trend, category and product analytics and anomaly alerts. The choice is remembered in the browser.

**Inventory intelligence.** Each store-product line is *critical* (under 1 day of cover), *low* (below reorder point), *healthy* or
*overstock* (above 2.5× reorder point), with a suggested order quantity that tops stock up to 3 days of average sales.

## 7. API

| Feature | Endpoint | Owner | Manager | Sales Exec | Admin |
|---|---|:-:|:-:|:-:|:-:|
| KPIs, trend, category, store, top products | `/sales/summary`, `/sales/trend`, `/sales/by-category`, `/sales/by-store`, `/sales/top-products` (all accept `?range=7d\|30d\|90d\|365d\|all`) | yes | yes | yes | yes |
| Low stock, inventory intelligence | `/inventory/alerts`, `/inventory/summary` | yes | yes | – | yes |
| Customer segments | `/segments`, `/segments/metrics`, `/segments/dendrogram` | yes | yes | yes | yes |
| Forecast | `/forecast/revenue` | yes | view | **no** | yes |
| Recommendations | `/recommendations/{customer_id}?product=` | yes | yes | yes | yes |
| Churn risk | `/churn/risk` | yes | yes | yes | yes |
| Anomaly alerts | `/anomalies` | yes | yes | – | yes |
| Model evaluation | `/models/performance` | yes | yes | – | yes |
| Excel report | `/reports/business` | yes | yes | – | yes |
| Invoices | `GET/POST /invoices`, `GET/PATCH /invoices/{id}` | view | view | create / update | create / update |
| Users | `/admin/users` | – | – | – | yes |
| Auth | `/register`, `/login`, `/auth/forgot-password`, `/auth/reset-password`, `/me`, `/health` | public | | | |

The forecast, invoice and user-management rows follow the access matrix from the project guide. **The other rows are my assumptions**; the whole
matrix lives in one dictionary, `ACCESS` in `backend/auth.py`. Interactive docs: http://localhost:8000/docs.

## 8. Machine-learning results

Measured from the files in `ml/outputs/` (`milestone4_test_results.csv`). XGBoost, Prophet and mlxtend were not installed in the environment
that generated the shipped outputs, so scikit-learn fallbacks were used and are named in the result tables. Install `requirements.txt` and run
`python ml\run_all.py` to regenerate with the real libraries.

| Module | Result |
|---|---|
| Segmentation | K-Means (K=4) silhouette 0.272, hierarchical 0.220, agreement between the two (ARI) 0.43, K-Means stability 0.985 |
| Forecasting | Time-based test on the last 146 days. Random Forest MAE 56,064, RMSE 71,586, MAPE 8.6%, R² −0.07. A simple "training average" baseline (RMSE 69,833) is as good or better |
| Recommendations | Collaborative filtering Precision@3 6.7% versus 3.2% for a popularity baseline (60-day holdout, 2,020 customers) |
| Churn | Logistic Regression selected: F1 0.791, ROC-AUC 0.817. Label = no purchase in the 90 days after a cutoff date |
| Anomalies | Isolation Forest on 150 injected anomalies: recall 0.79, precision 0.62, false-positive rate 2.4% |

**Why the forecast is weak.** Daily store revenue hovers around 677k ± 65k with no trend or weekly pattern, so no model can explain it. This is
reported as found, not hidden. **Churn label.** "Inactive for 90 days" used together with inactivity as a feature leaks the answer, so features are
built only from before a cutoff date.

## 9. Project structure

```
marketmindAI/
├── backend/       main.py (routes)  config.py  database.py  models.py  schemas.py  auth.py
│                  mailer.py  daterange.py  resettokens.py  init_db.py  load_data.py  .env.example  tests/
├── frontend/src/  App.jsx  M3Panels.jsx  M4Panels.jsx  Charts.jsx  api.js  App.css
├── ml/            segmentation.py  forecasting_models.py  forecasting_prophet.py  recommendations*.py
│                  churn_setup.py  churn_models.py  anomaly_detection.py  generate_reports.py
│                  test_models.py  verify_outputs.py  run_all.py  outputs/
├── datasets/      data_cleaning.py  data_cleaning_segmentation.py  data_quality_report.py  raw/  processed/
├── data/          marketmind.db is created here
├── docs/          ARCHITECTURE.md
├── MILESTONE_STATUS.md   TEST_REPORT.md
└── setup_windows.bat  start_backend.bat  start_frontend.bat  requirements*.txt
```

## 10. Setup (Windows, Python 3.11, Node 18+)

No PostgreSQL and no Docker needed.

```bat
cd marketmindAI
setup_windows.bat        :: one time: virtual env, packages, database, data load, npm install
start_backend.bat        :: terminal 1 - http://localhost:8000
start_frontend.bat       :: terminal 2 - http://localhost:5173
```

Then open http://localhost:5173. The admin account comes from `backend\.env` (`ADMIN_EMAIL`, `ADMIN_PASSWORD`). **Change the password.**
Create the other roles from the login page or from **Users** while logged in as admin.

Main settings in `backend\.env` (copy from `.env.example`):

| Setting | Purpose |
|---|---|
| `SECRET_KEY` | Signs login tokens. Use a long random value |
| `ADMIN_EMAIL`, `ADMIN_PASSWORD` | Admin created on first start |
| `ADMIN_REGISTRATION_CODE` | Code needed to sign up as Administrator (empty = disabled) |
| `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_FROM` | Sending reset e-mails (Gmail needs an App password) |
| `FRONTEND_URL` | Address put in the reset link |
| `REBASE_DATES_TO_TODAY` | `1` show recent dates, `0` real dates |

Re-run the data + ML pipeline: `python ml\run_all.py`. Tests: `cd backend && python -m pytest tests -v`.

## 11. Verification status

| Area | Status |
|---|---|
| Data cleaning, ML pipeline, Excel report, ML output files | Run and checked (see `TEST_REPORT.md`) |
| Dashboard behaviour (login, forgot-password form, admin role, name panel, date dropdown) | Checked in a real browser against a stand-in API; **not yet against the live backend** |
| Backend API, database, e-mail sending | Tests written (`backend/tests`); **run `pytest` on your machine and record the result here** |
| XGBoost, Prophet, mlxtend results | Not yet produced (fallbacks used) |
| Public deployment | Not done |

## 12. Known limitations

- The store data is synthetic-looking, so forecasts cannot beat a simple average.
- Dates on the dashboard are shifted forward by default (clearly labelled) so the sample data looks recent.
- SQLite suits one machine and a few users, not heavy concurrent use.
- Inventory figures are estimates derived from sales, not warehouse counts.
- Rows of the access matrix other than forecast, invoices and users are assumptions.
- Invoices are not linked to the sales rows or the Online Retail customers.
- Reset e-mails need SMTP settings; otherwise the link appears in the backend terminal.

## 13. Author

**Anubhav Kumar Gupta**
MarketMind AI internship project
