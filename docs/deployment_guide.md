# MarketMind AI — Deployment Guide & Infrastructure Specification

This document provides complete instructions for local containerized deployment via Docker and cloud hosting via **Vercel**, **Render**, or **Railway**.

### ⚡ Live Production URL (Vercel)
- **Live URL**: **[https://dist-one-wine-30.vercel.app](https://dist-one-wine-30.vercel.app)**
- **Deployment Status**: `READY` (Verified `HTTP 200 OK`)
- **Platform**: Vercel Edge Network
- **Build Output**: `frontend/dist` with client-side SPA routing rewrites

---

## 🐳 1. Local Containerized Deployment (Docker & Compose)

> [!NOTE]
> If running in an environment without Docker Desktop installed, install Docker Desktop for Windows/macOS or `docker.io` on Linux first.

### Prerequisites
- Docker Engine 24+ & Docker Compose v2+
- Port `8000` (FastAPI) and Port `8501` (Streamlit) available locally.

### Exact Execution Commands
```bash
# 1. Navigate to project root
cd /path/to/Infosys

# 2. Build and start containers in detached mode
docker compose up --build -d

# 3. View container status
docker compose ps

# 4. View real-time logs
docker compose logs -f

# 5. Stop containers
docker compose down
```

### Verified Local Endpoints
- **Streamlit Intelligence Dashboard**: `http://localhost:8501`
- **FastAPI Backend Root**: `http://localhost:8000`
- **Interactive Swagger Docs**: `http://localhost:8000/docs`
- **Health Check Probe**: `http://localhost:8000/health`

---

## ☁️ 2. Cloud Deployment (Render Free-Tier Guide)

MarketMind AI is optimized for Render's **Free Tier (512MB RAM)** using the included `start_unified.py` runner to prevent Out-Of-Memory (OOM) failures from heavy scientific libraries.

### 👤 MANUAL STEPS REQUIRED BY YOU (User Actions)
1. **Sign Up / Log In**: Go to [https://render.com](https://render.com) and sign in using your GitHub account.
2. **Push Your Repository**: Ensure your latest changes are pushed to your GitHub repository:
   ```bash
   git add .
   git commit -m "feat(deployment): add Docker, Railway, and Render deployment specifications"
   git push origin <your-branch-name>
   ```
3. **Create New Web Service**:
   - In Render Dashboard, click **New +** > **Web Service**.
   - Select **Build and deploy from a Git repository** and connect your GitHub repo.
4. **Configure Settings**:
   - **Name**: `marketmind-ai`
   - **Region**: Oregon (US West) or Frankfurt (EU)
   - **Branch**: Select your working branch (`milestone-2` or `main`)
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r backend/requirements.txt`
   - **Start Command**: `python start_unified.py`
   - **Instance Type**: `Free (512MB RAM)`
5. **Set Environment Variables**:
   Under the **Environment Variables** tab, add:
   - `PYTHON_VERSION`: `3.11.8`
   - `ENVIRONMENT`: `production`
6. **Click "Deploy Web Service"**.

---

## 🚂 3. Cloud Deployment (Railway Guide)

### 👤 MANUAL STEPS REQUIRED BY YOU (User Actions)
1. **Sign Up / Log In**: Go to [https://railway.app](https://railway.app) and log in with GitHub.
2. **New Project**: Click **New Project** > **Deploy from GitHub repo**.
3. **Select Repository**: Select `AI-Powered-Small-Business-Sales-Forecasting-and-Revenue-Growth-Intelligence-Platform`.
4. **Settings & Variables**:
   - Railway automatically reads [railway.json](file:///D:/Infosys/railway.json) and [Procfile](file:///D:/Infosys/Procfile).
   - In **Variables**, add:
     - `PYTHON_VERSION`: `3.11.8`
5. **Generate Domain**: In the service **Settings** tab, click **Generate Domain** under Networking.
6. Your live public URL will be ready in 2–3 minutes.

---

## 📋 4. Post-Deployment Verification Checklist

Once deployed to Render or Railway, verify that the live deployment behaves identically to local development:

| Test Item | Verification Procedure | Expected Live Result | Status |
| :--- | :--- | :--- | :---: |
| **1. UI Loading** | Open the live domain in your web browser. | Streamlit brand hero renders with role badge and tabs. | [ ] |
| **2. Health Check** | Navigate to `https://<live-url>/health` (or local API). | Returns `{"status":"healthy","database":"connected"}`. | [ ] |
| **3. RBAC Logins** | Click through the 4 quick-switch demo login buttons. | Each role logs in seamlessly; Store Manager gets locked store scope. | [ ] |
| **4. Executive 403** | Switch to **Sales Executive** and open **Sales Forecasting**. | Displays access restriction card; direct API returns HTTP 403. | [ ] |
| **5. Forecast Generation** | Switch to **Business Owner** and select 14-day horizon. | Spinner computes projection and renders Plotly timeline with confidence intervals. | [ ] |
| **6. Excel Report** | Click **📥 Download Report (30d)**. | File downloads as `MarketMind_Report_30d.xlsx` and opens with real data. | [ ] |
| **7. Customer 404** | Use the Instant Customer Lookup tool with `NONEXISTENT_999`. | Displays red `Customer Not Found (404)` message; valid ID shows profile. | [ ] |
