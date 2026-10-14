# MarketMind AI: Milestone 4 End-to-End Demo

This runbook demonstrates the verified local and Docker Compose flows without
claiming a cloud deployment. It uses the existing project data and does not
modify the evaluation CSV.

## 1. Verified startup commands

### Local development

From the repository root:

```powershell
.venv\Scripts\python.exe -m uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```

In a second terminal:

```powershell
Set-Location frontend
npm install
npm run dev
```

Open `http://localhost:5173`.

### Docker Compose

Set a local secret without committing it:

```powershell
$env:MARKETMIND_JWT_SECRET="<long-random-secret>"
docker compose up --build
```

Open `http://localhost:3000`. The verified Compose setup starts:

- `backend` on `http://localhost:8000`.
- `frontend` on `http://localhost:3000`.
- Nginx API proxy from frontend `/api/` to `backend:8000`.
- Persistent named volume `marketmind-data` for `/app/data`.

The backend container health check is:

```text
http://127.0.0.1:8000/health
```

Stop the demo with:

```powershell
docker compose down
```

## 2. Application walkthrough

1. Open the frontend URL.
2. Sign in with an authorized local development account configured by the
   application. Do not put real credentials in this document.
3. Confirm the dashboard loads sales, inventory, and customer summaries.
4. Review the segmentation panel and customer segment summaries.
5. Review the revenue forecast panel and model comparison.
6. Resize the browser to a narrow viewport and confirm cards and tables remain
   readable or scroll horizontally where required.
7. Sign out and confirm protected data is no longer available without a token.

The recommendation, churn, and anomaly implementations are available as
backend services and evaluation artifacts, but the current dashboard does not
claim to expose them as frontend panels where no corresponding API route
exists.

## 3. API checks

### Health and root

```powershell
Invoke-WebRequest http://localhost:8000/health -UseBasicParsing
Invoke-WebRequest http://localhost:8000/ -UseBasicParsing
```

Expected health response:

```json
{"status":"healthy"}
```

### Unauthenticated protection

```powershell
Invoke-WebRequest http://localhost:8000/api/auth/me -UseBasicParsing
```

Expected result: HTTP `401`.

### Login

Use an account supplied by the local development setup. Substitute the
credentials at runtime rather than storing them in this document:

```powershell
$body = @{
  email = "<authorized-local-email>"
  password = "<authorized-local-password>"
} | ConvertTo-Json

$login = Invoke-RestMethod `
  -Method Post `
  -Uri http://localhost:8000/api/auth/login `
  -ContentType "application/json" `
  -Body $body

$token = $login.access_token
$headers = @{ Authorization = "Bearer $token" }
```

### Authenticated reports

```powershell
Invoke-RestMethod http://localhost:8000/api/auth/me -Headers $headers
Invoke-RestMethod http://localhost:8000/api/sales/summary -Headers $headers
Invoke-RestMethod http://localhost:8000/api/customers/summary -Headers $headers
Invoke-RestMethod http://localhost:8000/api/segments -Headers $headers
Invoke-RestMethod http://localhost:8000/api/forecast/revenue -Headers $headers
```

The report responses are generated from the existing processed artifacts.
The revenue report contains a 30-row forecast and the segmentation report
contains summaries for the 300 processed customers.

### RBAC check

Use a token for a role that is not allowed to access a particular route and
confirm the backend returns HTTP `403`. The frontend displays a role-permission
message rather than leaving the page blank.

## 4. Evaluation results to mention during the demo

- Revenue Random Forest holdout RMSE: **163.801818**.
- Revenue Random Forest holdout MAE: **131.738268**.
- Revenue Random Forest holdout R²: **0.072599**.
- K-Means silhouette score: **0.434129**.
- Hierarchical silhouette score: **0.375785**.
- Recommendation Precision@3: **0.042222**.
- Recommendation Recall@3: **0.126667**.
- Churn metrics: unavailable because valid persisted row-level validation
  predictions and labels are absent.
- Anomaly fixture metrics: both detectors achieved 1.000000 accuracy and
  0.000000 false-positive rate on the controlled fixture only. These are not
  production estimates.

## 5. Troubleshooting

### Frontend cannot connect to the backend

- Confirm the backend is running on port 8000.
- For local development, confirm Vite is using its `/api` proxy.
- For Compose, confirm both services are running and the backend health check
  is passing.
- Check browser developer tools for the API status and user-facing error.

### Compose refuses to start

- Set `MARKETMIND_JWT_SECRET` in the current shell or `.env` file.
- Confirm Docker Desktop or another Docker engine is running.
- Run `docker compose config` to inspect expanded configuration.

### Database or processed data errors

- Confirm the processed CSV tree is present.
- Do not mount an empty `/app/data/processed` directory over the image data.
- Use a persistent `/app/data` volume for SQLite.
- Missing or invalid data produces a safe backend error; implementation
  details are logged server-side.

### Login fails

- Check the request uses `email` and `password`.
- Confirm the local database has been initialized.
- Confirm the token is sent as `Authorization: Bearer <token>`.
- A 401 means authentication failed or the token expired; a 403 means the
  authenticated role is not permitted for that route.

### Forecast or segmentation is empty

- Confirm `sales_forecast.csv`, `model_comparison.csv`, and
  `customer_segments.csv` exist under `data/processed`.
- Retry after confirming the backend has started successfully.
- Empty states are expected to show an explanatory message rather than a
  blank or crashing panel.

## 6. Demo boundaries

This demo verifies the documented local and Compose startup and API flows.
It does not verify a Render or Railway deployment, production credentials,
production anomaly labels, or a valid churn metric that the stored artifacts
cannot support.
