# MarketMind AI: Milestone 4, Days 7-8 Deployment Preparation

## Deployment architecture

The deployment configuration preserves the existing architecture:

- FastAPI serves the backend on port `8000`.
- React is built with Vite and served by Nginx on port `80` inside the frontend container.
- Nginx proxies `/api/` requests to the Compose `backend` service.
- SQLite is initialized from the processed CSV files during backend startup.
- The SQLite database is stored at the configurable `MARKETMIND_DATABASE_PATH`.

The configuration prepares the application for deployment; it does not claim that a cloud deployment has been performed.

## Local execution without Docker

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

Vite serves the frontend at `http://localhost:5173` and proxies `/api` to the local backend.

## Docker

Build and run the backend image from the repository root:

```powershell
docker build -t marketmind-backend .
docker run --rm -p 8000:8000 `
  -e MARKETMIND_JWT_SECRET="<long-random-secret>" `
  -e MARKETMIND_CORS_ORIGINS="http://localhost:3000" `
  -v marketmind-data:/app/data `
  marketmind-backend
```

The backend image installs dependencies from the existing `requirements.txt`, copies the processed datasets required by the application, and does not copy `.venv`, secrets, the local SQLite database, frontend dependencies, or build output.

Build the frontend image:

```powershell
docker build -t marketmind-frontend `
  --build-arg VITE_API_BASE_URL=/api `
  frontend
docker run --rm -p 3000:80 marketmind-frontend
```

The frontend Nginx configuration serves the SPA fallback and proxies `/api/` to `backend:8000` when used in Compose.

## Docker Compose

Create a local `.env` file that is not committed:

```text
MARKETMIND_JWT_SECRET=<long-random-secret>
```

Start both services:

```powershell
docker compose up --build
```

Open `http://localhost:3000`. The backend is also available at `http://localhost:8000`.

Stop the services:

```powershell
docker compose down
```

The Compose file uses:

- `backend` and `frontend` service names.
- A backend health check before the frontend starts.
- Port mappings `8000:8000` and `3000:80`.
- The named `marketmind-data` volume mounted at `/app/data`.
- A required `MARKETMIND_JWT_SECRET` environment variable.

## Environment variables

| Variable | Required | Purpose |
| --- | --- | --- |
| `MARKETMIND_JWT_SECRET` | Production | Secret used to sign JWTs. Never commit this value. |
| `MARKETMIND_DATABASE_PATH` | No | SQLite path. Defaults to the project `data/marketmind.db`; Compose uses `/app/data/marketmind.db`. |
| `MARKETMIND_CORS_ORIGINS` | No | Comma-separated allowed browser origins. |
| `PORT` | No | FastAPI listening port. Defaults to `8000`. |
| `VITE_API_BASE_URL` | Build-time | Frontend API prefix. Compose uses `/api`. |

If `MARKETMIND_JWT_SECRET` is omitted outside Compose, the current application generates a process-local random fallback. Production deployments should always set a stable secret so tokens are not invalidated on restart.

## Render or Railway preparation

### Backend service

- Root directory: repository root.
- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT`
- Health check path: `/health`
- Environment variables:
  - `MARKETMIND_JWT_SECRET`
  - `MARKETMIND_CORS_ORIGINS` set to the deployed frontend origin
  - `MARKETMIND_DATABASE_PATH` set to a mounted persistent-disk path if SQLite is retained

### Frontend service

- Root directory: `frontend`
- Build command: `npm ci && npm run build`
- Static output directory: `dist`
- Build-time variable: `VITE_API_BASE_URL` pointing to the deployed backend API prefix or URL.

For a separately hosted static frontend, configure `VITE_API_BASE_URL` to the backend URL and configure backend CORS to allow the exact frontend origin. The included Nginx configuration is intended for the Compose topology where `/api` is proxied internally.

## SQLite persistence and platform limitations

SQLite is file-based. Ephemeral container filesystems lose the database on restart or redeploy. The Compose named volume preserves `/app/data` locally, but production platforms require a persistent disk/volume mounted at the configured database directory.

The backend rebuilds SQLite tables from the copied or mounted processed CSV files during startup. Do not mount an empty `/app/data/processed` directory over the image data unless the complete processed dataset tree is supplied.

For multiple backend instances, SQLite is not an appropriate shared database without a shared filesystem and careful write coordination. A managed PostgreSQL database would be the production scaling path, but migrating the current application is outside this milestone.

## Validation performed

- React production build completed successfully with `npm run build`.
- Backend application import and reporting data checks completed using `.venv`.
- Backend Docker image build completed successfully.
- Frontend Docker image build completed successfully.
- Docker Compose started both services successfully.
- The backend container reported healthy through its Compose health check.
- The frontend was accessible at `http://localhost:3000`.
- The backend was accessible at `http://localhost:8000`.
- Manual application verification confirmed the running Compose application was usable.
- No deployment was performed or claimed.
- `data/processed/testing/milestone4_test_results.csv` was preserved.

The Docker runtime checks were performed after the initial preparation of this document. Exact image tags and container IDs are intentionally not recorded because they are local runtime details, not deployment configuration.
