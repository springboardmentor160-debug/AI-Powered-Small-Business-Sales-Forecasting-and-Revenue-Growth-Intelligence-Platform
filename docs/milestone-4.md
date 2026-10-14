# MarketMind AI — Milestone 4: Testing, Polish, Deployment

Final project documentation for the Small Business Sales Intelligence Platform.

## 1. What the platform does

| Layer | Technology | Purpose |
|---|---|---|
| Frontend | React 19, TypeScript, Vite, Recharts | Role-based dashboard (login, analytics, invoices, administration) |
| Backend | FastAPI, SQLAlchemy, JWT (HS256), bcrypt | Secured REST API with four roles |
| Database | PostgreSQL | Users, invoices, sales data, forecast results |
| AI modules | scikit-learn, XGBoost, Prophet | Forecasting, segmentation, recommendations, churn, anomaly detection |

Roles: `admin`, `business_owner`, `store_manager`, `sales_executive`. Access is enforced on the **backend** (`require_role`), not only hidden in the UI.

## 2. Testing the AI models (Day 1-4)

Reproduce everything with:

```bash
python -m backend.ml.run_milestone4_tests
```

Output: `artifacts/milestone-4/milestone4_test_results.csv` and `milestone4_test_report.md`.
All numbers are computed from the saved prediction/metric artifacts of Milestones 2 and 3 — nothing is typed in by hand.

### 2.1 Forecasting (chronological 80/20 test split)

| Model | MAE | RMSE | R² |
|---|---|---|---|
| Random Forest (UCI revenue) | 11,457.56 | 17,018.30 | **0.50** |
| XGBoost (UCI revenue) | 12,232.06 | 19,158.91 | 0.37 |
| Prophet (UCI revenue) | 20,117.51 | 27,568.77 | -0.31 |
| XGBoost (M5 demand, 28 days) | 21.72 | 25.17 | **0.457** |
| Random Forest (M5 demand) | 22.11 | 25.26 | 0.453 |
| Seasonal Naive baseline (M5) | 27.50 | 37.85 | -0.227 |

**Reading it:** R² of 0 means "no better than always guessing the average". Prophet scoring below 0 means it was *worse* than that on the test window, so it is not used for headline forecasts. Random Forest explains about half of the day-to-day revenue pattern on UCI; XGBoost is best on M5 demand. Both tree models clearly beat the seasonal-naive baseline (about 33% lower RMSE). Revenue is noisy, so an R² near 0.5 is a realistic result, not a failure.

### 2.2 Customer segmentation

| Method | k | Silhouette |
|---|---|---|
| K-Means | 4 | 0.5725 |
| Hierarchical | 4 | 0.5945 |

Sensitivity to the number of clusters: k=2 → 0.892, k=3 → 0.894, k=4 → 0.573, k=5 → 0.578, k=6 → 0.550.

**Honest note:** k=2 and k=3 score higher, but their smallest cluster has only 60 and 25 customers respectively (one giant cluster holds about 5,800), which makes the segments less useful to a business. k=4 was kept deliberately because it gives distinct, actionable groups while still scoring above 0.5 (reasonable structure). See `k3_k4_business_comparison.csv`.

### 2.3 Churn prediction (1,049 held-out customers)

Selected model: **Random Forest**.

| Metric | Random Forest | XGBoost | Logistic Regression |
|---|---|---|---|
| Accuracy | **0.771** | 0.746 | 0.741 |
| Precision | 0.770 | 0.748 | 0.750 |
| Recall | 0.848 | 0.831 | 0.811 |
| F1-Score | 0.807 | 0.787 | 0.779 |
| ROC-AUC | 0.826 | 0.822 | 0.815 |

A model that always predicts "churn" would score 0.436 accuracy, so 0.771 is a genuine improvement. Recall (0.85) matters most here: missing a customer who is about to leave costs more than a false alarm.

### 2.4 Recommendations (top-10 lists, 2,285 customers, holdout from 2011-09-10)

| Model | Precision@10 | Recall@10 | Hit rate@10 |
|---|---|---|---|
| Collaborative filtering | **0.0579** | **0.0183** | **0.357** |
| Popularity baseline | 0.0394 | 0.0114 | 0.279 |

Collaborative filtering beats "just recommend what's popular" by about 47% on precision and 28% on hit rate. Absolute values are low because each customer buys only a few of thousands of products in the holdout window; the comparison to the baseline is the meaningful result.

### 2.5 Anomaly detection (no real fraud labels exist)

Method: 150 real invoices were copied and inflated 20-80x (quantity and value), mixed with 39,206 real invoices, and scored by the same Isolation Forest used in production (`contamination=0.005`).

| Metric | Value |
|---|---|
| Detection accuracy | 99.42% |
| Recall (injected cases caught) | 38.0% |
| Precision | 29.5% |
| False positive rate | 0.35% (upper bound) |

**Honest note:** the 99.4% accuracy is misleading on its own, because 99.6% of invoices are normal. The more truthful numbers are recall (38%) and precision (30%). The detector is deliberately strict (it flags about 0.5% of invoices), and real unusual invoices already in the data outrank many injected ones. The false-positive rate is an upper bound because genuinely odd real invoices count as "false alarms". Raising `contamination` or combining with the z-score flag would raise recall at the cost of more alerts — a business trade-off recorded for future work.

## 3. Polish and graceful failure (Day 5-6)

| Area | Change |
|---|---|
| Backend: missing data file | Returns **503** "temporarily unavailable" instead of a traceback (`FileNotFoundError`, `EmptyDataError` handlers) |
| Backend: unexpected errors | Middleware returns a calm **500** message; details only in server logs; CORS headers preserved so the browser can show it |
| Backend: unknown record | 404 with a clear message (existing endpoints) |
| Frontend: slow/unreachable server | 20-second request timeout; separate messages for "too slow" and "can't connect" |
| Frontend: status codes | Friendly text for 401 / 403 / 404 / 500 / 503 |
| Frontend: session expiry | A 401 signs the user out with "Your session has expired" |
| Frontend: one broken screen | `ErrorBoundary` shows "This section hit a problem" + Try again; the rest of the app keeps working |
| Frontend: loading | Skeleton rows on tables, spinner on refresh, no frozen screens |
| Frontend: errors | Inline error with a **Retry** button on Invoices and Administration |
| Frontend: offline | Red banner when the browser loses its connection |
| Frontend: live health | Heartbeat pings `/health` every 5 s and charts real latency |

### End-to-end checklist (run before every demo)

| Check | How | Expected |
|---|---|---|
| Login per role | Sign in as each of the four roles | Each role sees only its allowed pages |
| Restricted access | As sales executive, call an admin endpoint | 403 "no permission" message, no crash |
| Fresh dashboard | Open the dashboard | All panels load, or show a calm error |
| Backend down | Stop the API, reload | "Couldn't reach MarketMindAI" + live badge turns OFFLINE |
| Slow section | Reload Forecasts | Loading state, then results |
| Invoice flow | Create New Invoice → Download | Row appears; file opens with correct data |
| Admin flow | Add / Edit / Update / Delete a user | Table updates; cannot delete or demote yourself |
| Session expiry | Use an expired token | Returned to login with an explanation |

## 4. Deployment (Day 7-8)

See `docs/deployment.md` for step-by-step instructions. Summary:

- `Dockerfile` (API), `frontend/react-app/Dockerfile` (nginx), `docker-compose.yml` (db + api + web)
- `render.yaml` blueprint for Render; manual steps for Railway
- `requirements-api.txt`: a slim runtime set (no Prophet / Streamlit / pytest)
- `docker-entrypoint.sh`: creates tables, seeds the first admin from `ADMIN_EMAIL` / `ADMIN_PASSWORD`, starts uvicorn on `$PORT`

## 5. Known limitations and future work

- Deployment files were written and syntax-checked but not executed against a live Docker daemon or cloud account in the authoring environment; follow the verification checklist in `docs/deployment.md`.
- Anomaly detection recall is modest (see 2.5); tune `contamination` with real labelled cases when available.
- Forecast quality is limited by noisy daily revenue; adding promotions/holiday features is the next step.
- Passwords are stored only as bcrypt hashes and cannot be displayed — by design.
- Free-tier cloud services sleep when idle; open the API URL a minute before a demo.
