# MarketMind AI: Milestone 4 Days 9-10 Final Documentation

## 1. Project summary

MarketMind AI is a small-business sales forecasting and revenue-growth
intelligence platform. The completed application preserves the FastAPI +
React + SQLite architecture and adds analytics for forecasting, customer
segmentation, churn risk, recommendations, and anomaly indicators.

Milestone 4 Days 9-10 consolidates the implemented functionality, measured
results, deployment preparation, and known limitations. The evaluation
results are preserved in
`data/processed/testing/milestone4_test_results.csv`.

## 2. Architecture

The system has four primary runtime layers:

1. **React/Vite frontend:** authenticated dashboard, sales summaries,
   segmentation display, revenue forecast display, model comparison, loading
   states, empty states, and user-facing errors.
2. **FastAPI backend:** authentication, role-protected summary/report routes,
   service error translation, CORS configuration, and health checks.
3. **Analytics services:** existing forecasting, segmentation, churn,
   collaborative-filtering recommendation, anomaly, and reporting services.
4. **SQLite and processed data:** application users and business summaries are
   stored in SQLite; generated analytics and source-derived processed CSV
   artifacts remain under `data/processed`.

For containerized execution, the backend runs on port 8000. The React
application is built into an Nginx image, served on container port 80, and
published on port 3000 by Compose. Nginx proxies `/api/` requests to the
Compose `backend` service.

## 3. Datasets and artifacts

The evaluation and application use the existing processed artifacts; the
original datasets were not modified.

| Artifact or dataset | Actual size/use |
| --- | ---: |
| Cleaned sales transactions | 12,000 single-product transactions |
| Cleaned customers | 300 customers |
| Product universe | 24 products |
| Cleaned inventory | 96 inventory rows |
| Customer segmentation output | 300 customers |
| Forecast validation predictions | 180 rows: 30 rows for each model-target pair |
| Forecast validation period | 2025-12-02 through 2025-12-31 |
| Consolidated Milestone 4 results | 30 rows |

The model-testing evaluator reads persisted outputs rather than rebuilding
models. Forecasting uses
`data/processed/forecast/model_validation_predictions.csv`.
Segmentation uses `data/processed/segments/customer_segments.csv` and the
existing customer feature preparation.

## 4. Models and actual evaluation results

### Forecasting

Forecasting was evaluated on the same chronological 30-day holdout for
Prophet, XGBoost, and Random Forest. Revenue and sales quantity were evaluated
separately using MAE, RMSE, and R².

| Target | Model | MAE | RMSE | R² |
| --- | --- | ---: | ---: | ---: |
| Revenue | Prophet | 139.280055 | 167.841098 | 0.026297 |
| Revenue | XGBoost | 141.439689 | 178.166143 | -0.097186 |
| Revenue | Random Forest | 131.738268 | 163.801818 | 0.072599 |
| Sales quantity | Prophet | 5.904611 | 7.662424 | 0.051746 |
| Sales quantity | XGBoost | 6.536274 | 8.284615 | -0.108504 |
| Sales quantity | Random Forest | 6.128144 | 7.903255 | -0.008798 |

Random Forest has the lowest measured revenue MAE and RMSE. Prophet has the
lowest measured sales-quantity MAE and RMSE. These are holdout results, not a
claim that either model will remain best on future data.

### Customer segmentation

The existing three-cluster labels were evaluated with the existing
`log1p` + `StandardScaler` feature preparation and customer ordering.

| Model | Customers | Clusters | Silhouette Score |
| --- | ---: | ---: | ---: |
| K-Means | 300 | 3 | 0.434129 |
| Hierarchical | 300 | 3 | 0.375785 |

### Churn

Accuracy, precision, recall, and F1-score are recorded as unavailable. The
persisted `churn_predictions_final.csv` contains full-dataset predictions, not
row-level validation predictions paired with ground-truth labels. Scoring
those predictions would leak training data, so no churn metric was fabricated.

### Recommendations

Collaborative filtering was evaluated with K=3 using a temporal
leave-last-transaction-out holdout:

- Training rows: 11,700.
- Held-out rows: 300.
- Customers evaluated: 300.
- Precision@3: **0.042222**.
- Recall@3: **0.126667**.

The held-out transactions were excluded from recommendation generation.

### Anomaly detection

The original data has no verified anomaly labels. The reported controlled
fixture results are not production performance estimates:

| Detector | Fixture | Detection Accuracy | False Positive Rate |
| --- | --- | ---: | ---: |
| Z-score | 100 labeled normal, 2 labeled anomalous rows | 1.000000 | 0.000000 |
| Isolation Forest | 100 labeled normal, 2 labeled anomalous rows | 1.000000 | 0.000000 |

The original unlabeled outputs contain 512 Z-score detections and 120
Isolation Forest detections. Those counts are not confirmed anomalies.

## 5. Frontend and backend functionality

The React frontend provides:

- Login and logout flow.
- Dashboard summaries for sales, inventory, and customers.
- Customer segmentation display.
- Revenue forecasting and model comparison display.
- Loading, empty, timeout, network-error, unauthorized, and forbidden states.
- Responsive card, table, navigation, and chart-related layout behavior.

The FastAPI backend provides:

- `GET /health` and `GET /`.
- `POST /api/auth/login`.
- `POST /api/auth/logout`.
- `GET /api/auth/me`.
- Protected sales, inventory, customer, segmentation, and revenue forecast
  routes.

Churn, recommendation, and anomaly functionality exists as backend services
and evaluation code. No claim is made that those services are exposed as
frontend dashboard routes when no equivalent API route exists.

## 6. Authentication and RBAC

Authentication uses short-lived JWT bearer tokens signed with
`MARKETMIND_JWT_SECRET`. Passwords are stored using salted `scrypt` hashes.
The backend checks that the user still exists when decoding a token.

The supported roles are:

- Business Owner.
- Store Manager.
- Sales Executive.
- System Administrator.

Route dependencies enforce role access. The frontend preserves the backend's
401 and 403 responses and displays session-expiry or permission messages.
Production deployments must set a stable secret; the process-local fallback
is intended only for non-production use.

## 7. Testing and validation

Completed checks include:

- Python syntax/import checks for modified backend code.
- Backend reporting/import smoke checks using the existing `.venv`.
- Live FastAPI health and protected-route smoke checks.
- React production build with `npm run build`.
- Backend Docker image build.
- Frontend Docker image build.
- Docker Compose startup for backend and frontend.
- Backend container health check.
- Manual access to frontend `http://localhost:3000`.
- Manual access to backend `http://localhost:8000`.
- Preservation of the 30-row evaluation CSV.

The in-process FastAPI test client was not used because the environment lacked
the optional compatible HTTP client dependency; live Uvicorn/HTTP checks were
used instead.

## 8. Docker and deployment preparation

The repository includes:

- Root backend `Dockerfile`.
- Frontend multi-stage `frontend/Dockerfile`.
- `frontend/nginx.conf` with SPA fallback and `/api/` proxying.
- `docker-compose.yml` with health dependency and a named
  `marketmind-data` volume.
- `.dockerignore` excluding virtual environments, secrets, bytecode, local
  databases, and generated frontend output.

Compose validation has been completed successfully. This is deployment
preparation only: no Render or Railway cloud deployment has occurred.

SQLite requires persistent storage in production. The Compose volume protects
the local containerized database, but an ephemeral cloud filesystem will lose
data after restart or redeploy. Multiple backend replicas also require a
different shared database strategy.

## 9. Setup instructions

### Local development

Backend:

```powershell
.venv\Scripts\python.exe -m uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```

Frontend, in a second terminal:

```powershell
Set-Location frontend
npm install
npm run dev
```

### Docker Compose

Set a secret in a local, uncommitted environment file or shell:

```powershell
$env:MARKETMIND_JWT_SECRET="<long-random-secret>"
docker compose up --build
```

Open `http://localhost:3000`. The backend health endpoint is
`http://localhost:8000/health`.

Stop the stack with:

```powershell
docker compose down
```

See [milestone4_day7_8_deployment.md](./milestone4_day7_8_deployment.md) for
Render/Railway preparation and environment-variable details.

## 10. Limitations

- Forecast scores use one 30-day chronological holdout.
- Churn metrics cannot be validly calculated from the persisted artifacts.
- Recommendation metrics use one temporal holdout and K=3.
- Anomaly metrics are controlled-fixture results, not real-world performance.
- Original anomaly detections have no verified labels.
- Churn, recommendation, and anomaly services do not all have corresponding
  frontend/API routes.
- SQLite is not suitable for uncoordinated multi-instance production writes.
- No cloud deployment or production traffic validation has occurred.

## 11. Future improvements

1. Persist a leakage-free churn validation split with row-level labels and
   predictions, then report class-balanced metrics and a confusion matrix.
2. Collect verified anomaly labels and evaluate detectors on representative
   production-like data.
3. Add authenticated API routes and UI panels for recommendations, churn, and
   anomaly review where product scope requires them.
4. Run rolling or multiple-period forecast backtests.
5. Add automated browser and API integration tests with a pinned compatible
   test-client dependency.
6. Migrate to a managed relational database before horizontal scaling.
7. Add observability, model drift monitoring, and scheduled model refreshes.
