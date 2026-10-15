# Milestone status

## Important: official requirements were not available

The uploaded ZIP contains **no milestone instruction documents** (no PDFs, guides or rubrics - only code, data and a README that mentions an
"internship guide"). Therefore the requirement lists below are **reconstructed** from (a) the README and code comments of the original project,
which refer to the guide's steps, and (b) your request. They are **not** the official checklists. Please compare them against the real documents.
In particular I could not determine: whether **Spring Boot** is mandatory, what Milestone 4's deliverables are (presentation? report? demo video?),
and the full role/access matrix beyond the rows quoted in the original README.

Legend: **Verified** = run in this session · **Written, not run** = implemented and statically checked, but the environment had no internet to
install FastAPI/SQLAlchemy/npm (see `TEST_REPORT.md`) · **Missing** = not done · **Unknown** = depends on the official text.

## Milestone 1 - data, database, API, frontend, auth (reconstructed)

| Requirement | Implementation | Status / evidence |
|---|---|---|
| Data collection, cleaning, duplicates, missing values | `datasets/data_cleaning.py`, `data_cleaning_segmentation.py`; processed CSVs shipped | **Verified**: both scripts re-run on the included raw files, reproducing the processed CSVs exactly; `data_quality_report.py` → 0 missing, 0 duplicates, 0 invalid |
| Synthetic vs real data stated honestly | README "Data", `data_quality.json` provenance notes | **Done** - store data flagged as most likely synthetic; Online Retail II is real |
| Database schema + loading (SQLite) | `models.py`, `database.py`, `config.py`, `init_db.py`, `load_data.py` | **Written, not run**. Load transformation partly verified |
| Backend API + error handling | `main.py` (503 messages for missing data/DB, 404, 422, 403) | **Written, not run**; 13 pytest tests ready |
| Registration, login, JWT, protected endpoints, roles | `auth.py`, `/register`, `/login`, `/me`, `ACCESS` matrix | **Written, not run** (tests cover 401/403, admin creation block, deleted-user token) |
| Frontend pages, dashboards, charts, navigation, loading/empty/error states | `frontend/src/*` (login/register, KPIs, trend+forecast chart, bar charts, tables, per-role views) | JSX syntax **Verified**; build/run **not tested** |
| Documentation, architecture, setup, demo readiness | `README.md`, `docs/ARCHITECTURE.md`, Windows `.bat` scripts | **Done**; scripts not run on Windows |

## Milestone 2 - segmentation and forecasting

| Requirement | Implementation | Status / evidence |
|---|---|---|
| RFM features | `common.customer_features`, `segmentation.py` (R/F/M + quartile scores) | **Verified** (`segment_assignments.csv`) |
| Scaling | log1p → StandardScaler | **Verified** |
| K-Means + justified K | K=2..7 silhouette, inertia, Davies-Bouldin, Calinski-Harabasz; K=4 with written justification | **Verified** - silhouette favours K=2; choice of K=4 is a business decision, stated as such |
| Hierarchical + dendrogram | Ward linkage, `dendrogram.png` with K-cut line | **Verified** |
| Silhouette, ARI | silhouette 0.272 / 0.220, ARI 0.430, seed-stability 0.985 | **Verified** |
| Cluster summaries / interpretation | `segments.json` (`business_interpretation`, `recommended_action`) | **Verified** |
| Daily aggregation, missing dates | `forecasting_models.daily_revenue` (reindex + interpolation, count reported; 0 gaps in data) | **Verified** |
| Time-based split, leakage-free lags/rolling | date-based 80/20 split; features built row-by-row from earlier days only | **Verified** |
| Random Forest | MAE 56,064, RMSE 71,586, MAPE 8.6%, R² −0.07 | **Verified** |
| XGBoost | code path exists (`common.make_regressor`) | **Not run** - xgboost not installed; fallback gradient boosting measured (RMSE 74,562) and labelled as such. Re-run `python ml\run_all.py` after `pip install -r requirements.txt` |
| Prophet | `forecasting_prophet.py` (same test window) | **Not run** - prophet not installed |
| Outputs connected to backend/frontend | `/forecast/revenue`, `/segments*`, dashboard panels, `verify_outputs.py` | Output contract **Verified**; HTTP layer **not run** |

Honest finding: the store dataset has no learnable signal; a constant (training mean) baseline beats both models. This is reported, not hidden.

## Milestone 3 - analytics, inventory, recommendations, churn, anomalies, reports, invoices (reconstructed)

| Requirement | Implementation | Status |
|---|---|---|
| Sales & revenue analytics | `/sales/summary`, `/trend`, `/by-category`, `/by-store`, `/top-products`; dashboard panels | Written, not run |
| Inventory alerts + intelligence | `/inventory/alerts`, `/inventory/summary` (days of cover, status, suggested order qty - heuristic) | Written, not run (SQL logic covered by a test with hand-computed values) |
| Recommendations | collaborative filtering + association rules (`recommendations*.py`), `/recommendations/{id}` | ML **Verified** (Precision@3 6.7% vs 3.2% baseline); mlxtend Apriori not run (exact fallback used) |
| Churn-risk prediction | `churn_setup.py`, `churn_models.py`, `/churn/risk`; leakage-free label | **Verified** (LR F1 0.791, ROC-AUC 0.817) |
| Anomalies | Z-score + Isolation Forest, `/anomalies` | **Verified** (recall 0.79 / precision 0.62 on injected anomalies) |
| Business reports | `business_report.xlsx`, `/reports/business` | File **Verified**; endpoint not run |
| Invoices | `POST/GET /invoices`, `GET/PATCH /invoices/{id}` | Written, not run |
| Spring Boot | **Not implemented.** The project is FastAPI; requirement unknown | **Unknown** - see `docs/ARCHITECTURE.md` for the integration approach if mandatory |

## Milestone 4 (instructions unavailable)

I did **not** receive the official Milestone 4 instructions, so I cannot mark it complete. What exists, based on the original project's own "M4" scripts:

| Item | Implementation | Status |
|---|---|---|
| Measured model results table | `ml/test_models.py` → `ml/outputs/milestone4_test_results.csv` (forecast MAE/RMSE/MAPE/R², silhouette, ARI, churn, recsys, anomalies) | **Verified** |
| Evaluation dashboard | `/models/performance`, "Model performance" panel (admin/owner/manager) | Written, not run |
| Testing documentation | `TEST_REPORT.md`, `backend/tests`, `ml/verify_outputs.py` | Done; backend tests not run |
| Project documentation / demo readiness | `README.md`, `docs/ARCHITECTURE.md`, Windows scripts | Done |
| Presentation / demo video / final report / deployment | - | **Missing / Unknown** - need the official M4 text |
