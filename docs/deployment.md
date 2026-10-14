# Deployment guide

## A. Run everything locally with Docker

1. Install Docker Desktop.
2. In the project root create a `.env` file (copy `.env.example`) and set at least `SECRET_KEY` and `ADMIN_PASSWORD`.
3. Run:
   ```bash
   docker compose up --build
   ```
4. Open **http://localhost:8080** and sign in with `ADMIN_EMAIL` / `ADMIN_PASSWORD`. API docs: http://localhost:8000/docs.

First start takes a few minutes (it downloads Postgres and installs dependencies).

## B. Deploy on Render (recommended)

1. Push the project to GitHub. Make sure `.env` is **not** committed.
   The UCI files in `backend/data/raw/uci/` (about 90 MB) must be in the repo or the live sales summary will show "N/A"; the 400 MB `backend/data/raw/m5/` folder is not needed.
2. Render dashboard → **New → Blueprint** → select the repo. It reads `render.yaml` and creates a Postgres database, the API and the static frontend.
3. When asked, enter `ADMIN_EMAIL` and `ADMIN_PASSWORD`. Leave the two URL variables empty for now.
4. After the first deploy, copy the two URLs Render shows:
   - API service → set **`CORS_ALLOWED_ORIGINS`** = the frontend URL (e.g. `https://marketmind-web.onrender.com`)
   - Frontend service → set **`VITE_API_BASE_URL`** = the API URL (e.g. `https://marketmind-api.onrender.com`), then **Manual Deploy → Clear build cache & deploy** (this value is baked in at build time).
5. Open the frontend URL and sign in.

## C. Deploy on Railway

1. New Project → **Deploy from GitHub repo** (API service uses the root `Dockerfile` automatically).
2. **Add → Database → PostgreSQL**. In the API service variables add `DATABASE_URL` = reference to the Postgres `DATABASE_URL`, plus `SECRET_KEY`, `ADMIN_EMAIL`, `ADMIN_PASSWORD`, and `CORS_ALLOWED_ORIGINS` (frontend URL).
3. Add a second service from the same repo with **Root Directory** `frontend/react-app` (uses its Dockerfile). Set the build variable `VITE_API_BASE_URL` to the API's public URL.
4. Generate public domains for both services.

## Verifying a deployment

| Check | Expected |
|---|---|
| `<api-url>/health` | `{"status":"healthy",...}` |
| `<api-url>/docs` | Swagger UI lists `/admin/users`, `/invoices/...` |
| Frontend loads | Login page with the animated background |
| Sign in as admin | Dashboard; the LIVE badge shows API latency |
| Invoices → Create New Invoice | Saves and the row appears |
| Administration → Add user | New user persists after refresh |

## Troubleshooting

| Symptom | Likely cause / fix |
|---|---|
| Browser shows "Couldn't reach MarketMindAI" | Wrong `VITE_API_BASE_URL`, or `CORS_ALLOWED_ORIGINS` doesn't match the frontend URL exactly (no trailing slash) |
| Sales summary shows N/A | UCI raw CSVs missing from the deployed image |
| Everyone is signed out after each deploy | `SECRET_KEY` not set (a random one is generated per start) |
| Cannot sign in on a fresh database | `ADMIN_EMAIL` / `ADMIN_PASSWORD` not set, so no admin was seeded |
| First request takes about 50 seconds | Free tier was asleep; wait and retry |
