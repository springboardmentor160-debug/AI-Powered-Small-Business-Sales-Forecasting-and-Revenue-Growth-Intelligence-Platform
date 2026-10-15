# Test report

Date of testing: 2026-10-13. **Read this first:** the environment used to modify this project had **no internet access**, so Python packages
(FastAPI, SQLAlchemy, XGBoost, Prophet, mlxtend) and npm packages could not be installed. Consequently **the backend, the SQLite layer and the
frontend build were NOT executed here.** They were written carefully and statically checked, and the exact commands to run them on your
machine are below. Everything marked PASS was actually run.

Environment used: Linux, Python 3.12.3, pandas 3.0.2, scikit-learn 1.8.0, SciPy 1.17.1, matplotlib 3.10.8, openpyxl 3.1.5, Node 22 + TypeScript compiler.
Target environment (your PC): Windows, Python 3.11.

## Summary

| Area | Status | Evidence |
|---|---|---|
| Python syntax of all backend / ml / datasets files | **PASS** | `python -m compileall backend ml datasets` |
| Data cleaning on the raw files (`data_cleaning.py`, `data_cleaning_segmentation.py`) | **PASS** | run on the supplied raw files: 73,100 → 73,100 rows; 1,067,371 → 776,854 rows (243,007 missing CustomerID, 34,335 duplicates removed); outputs byte-identical to the previously shipped processed CSVs |
| Data-quality report on processed datasets | **PASS** | `python datasets/data_quality_report.py` → store data: 73,100 rows, 0 missing, 0 duplicates, 0 invalid, 731 days with no calendar gaps; online retail: 776,854 rows, 0 missing, 0 duplicates, 0 invalid |
| ML pipeline end to end (`python ml/run_all.py`) | **PASS** (11 steps ran, Prophet step skipped: not installed) | segmentation, forecasting, recommendations, churn, anomalies, report and M4 results regenerated without errors |
| ML output contract (`python ml/verify_outputs.py`) | **PASS** | all files the API/dashboard read exist and contain the fields they use |
| Excel report content | **PASS** | `business_report.xlsx` sheets: Customer Segments, Sales Forecast, Model Comparison, Top Churn Risk (100 rows), Anomaly Alerts (200 rows) |
| `load_data.py` NaN→NULL / native-type conversion | **PASS (partial)** | the pandas transformation was run on the real CSV (ints, floats, strings, `date` all native Python types, NaN → `None`). The SQLAlchemy insert itself was not run |
| Frontend JSX syntax | **PASS** | TypeScript parser over `src/*.jsx`, `src/*.js` (the checker was confirmed to detect a deliberate syntax error). This is **not** a Vite build |
| Frontend production build / dev server | **NOT TESTED** | no npm registry. Run `cd frontend && npm install && npm run build` |
| Dependency installation (`pip install`, `npm install`) | **NOT TESTED** | no internet. Package pins are in `requirements*.txt` / `package.json` |
| Database initialisation (`init_db.py`) on SQLite | **NOT TESTED** | needs SQLAlchemy. Run `cd backend && python init_db.py` |
| Backend startup, `/health` | **NOT TESTED** | needs FastAPI. Run `start_backend.bat`, open `/health` |
| Registration, login, JWT, role checks, sales, inventory, invoices, admin | **NOT TESTED** (tests written, 13 test functions in `backend/tests/test_api.py`) | run `cd backend && python -m pytest tests -v` |
| Windows `.bat` scripts | **NOT TESTED** | written for CMD; never executed on Windows |
| Prophet and XGBoost results | **NOT TESTED** | not installed; the pipeline used scikit-learn gradient boosting as an explicitly named fallback and skipped Prophet |
| mlxtend Apriori | **NOT TESTED** | the exact pair-counting fallback produced `association_rules.csv` |

## Measured ML results (from this run)

See README "ML results". Nothing was estimated or copied from earlier documentation: forecasting, segmentation and the M4 results table were
re-generated in this run (and differ from the old README for forecasting because the evaluation was rebuilt - see below); churn, recommendations and
anomaly numbers reproduced the previous values.

## Problems found and fixed while inspecting the project

1. **Forecast comparison was not like-for-like:** Prophet's test window (last 20% of 731 rows) differed from the ML models' (last 20% of 724 rows after lag warm-up). All models now share one date-based window; baselines (same weekday last week, training mean) and MAPE were added. This revealed that a training-mean baseline beats both ML models.
2. **Segmentation "method agreement" compared cluster *names*, not partitions.** Added the Adjusted Rand Index (0.430), Davies-Bouldin, seed-stability ARI, inertia per K and a written, data-checked justification of K=4 (silhouette favours K=2).
3. **`SECRET_KEY` could be read before `.env` was loaded** (import-order dependent). Configuration now lives in `backend/config.py` and loads `.env` first.
4. **Deleting a user who created invoices would fail** once SQLite foreign keys are enabled. Invoices are now kept (`created_by` set to NULL).
5. **Tokens of deleted users stayed valid** until expiry; every request now re-reads the user and role from the database.
6. **passlib/bcrypt version conflict** (pinned `bcrypt==4.0.1`) removed: `bcrypt` is used directly, which is hash-compatible with the old passlib hashes.
7. **NaN values in CSV-backed endpoints** could break JSON serialisation; they are now converted to `null`.
8. `run_all.sh` only worked in bash; added a cross-platform `ml/run_all.py` that skips steps whose raw inputs are missing.
9. A duplicate-email race on registration returned a 503; it now returns 400.

## Commands to run the untested parts (Windows CMD)

```bat
setup_windows.bat
cd backend
python -m pytest tests -v
python init_db.py
python load_data.py
uvicorn main:app --port 8000
:: in another window
curl http://localhost:8000/health
cd ..\frontend
npm run build
```
Please send me any failing output - the backend and frontend were not run by me, so a first-run error is possible.
