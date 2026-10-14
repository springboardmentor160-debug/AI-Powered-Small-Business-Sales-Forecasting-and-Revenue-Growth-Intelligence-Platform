# MarketMind AI — Milestone 4: Production Web Application Deployment

> **Enterprise Sales Forecasting, RFM Customer Segmentation, Product Recommendations, Churn Prediction, Anomaly Detection & Real-Time Dataset Ingestion Platform**

---

## 🌟 Overview & Architecture

**MarketMind AI Milestone 4** is the production-ready integration release of the MarketMind AI web application. It combines high-performance machine learning models, interactive multi-role analytics dashboards, and a robust FastAPI backend ready for seamless serverless deployment to **Vercel** via GitHub integration.

### Application Highlights:
- **Role-Based Access Control (RBAC):** Tailored, permission-aware dashboards for **Business Owner**, **Store Manager**, **Sales Executive**, and **Administrator**.
- **Time-Series Sales Forecasting:** Prophet, Random Forest, and XGBoost revenue trend predictions with confidence intervals and interactive comparison tools.
- **RFM Customer Segmentation:** K-Means clustering dividing customers into Champions, Loyalists, At Risk, and Hibernating tiers.
- **AI Recommendation Engine:** Dual-engine architecture combining Collaborative Filtering cosine similarity and Apriori Association Rules (Market Basket Analysis).
- **Customer Churn Risk Stratification:** Machine learning classification predicting churn risk probabilities with actionable retention strategies.
- **Transaction & Inventory Anomaly Detection:** Isolation Forest and Z-Score statistics uncovering outliers, high-risk refunds, and unusual surges.
- **Universal Dataset Ingestion:** Real-time upload interface supporting custom CSV and Excel retail sales datasets, instantly normalizing schemas and recomputing intelligence across all role views.

---

## 📁 Milestone 4 Project Directory Structure

```text
Milestone_4/
├── api/
│   ├── __init__.py
│   └── index.py                      # Vercel Serverless Function entrypoint
├── backend/
│   ├── __init__.py
│   ├── auth.py                       # JWT token authentication & PBKDF2-HMAC password hashing
│   ├── database.py                   # SQLAlchemy engine with Vercel /tmp persistence handling
│   ├── db_models.py                  # Database ORM models
│   ├── db_service.py                 # Schema initialization & demo database seeding
│   ├── insights.py                   # Natural language AI strategic summary generators
│   ├── main.py                       # FastAPI application entrypoint & static mount
│   ├── models.py                     # Pydantic request/response schemas
│   ├── pipeline.py                   # Universal dataset normalization & ML pipeline
│   └── routes.py                     # Dual-mounted API endpoints (/api and root)
├── data/
│   ├── clean_inventory.csv           # Inventory benchmark dataset
│   ├── clean_sales.csv               # Historical sales dataset
│   └── sample_sales_upload.csv       # Sample retail file ready for upload testing
├── frontend/                         # Source frontend assets
│   ├── app.js                        # Complete UI state & Chart.js visualization engine
│   ├── index.css                     # Premium Glassmorphism & responsive CSS design
│   └── index.html                    # Unified role-switching web dashboard
├── outputs/                          # ML models evaluation, predictions & reports
│   ├── anomalies/                    # Transaction & inventory anomaly metrics
│   ├── churn/                        # Customer churn scores & risk metrics
│   ├── forecasting/                  # Multi-model forecasts & evaluation scores
│   ├── recommendations/              # Collaborative recommendations & association rules
│   ├── reports/                      # Strategic executive reports in Markdown
│   └── segmentation/                 # RFM cluster profiles & customer mapping
├── public/                           # Vercel CDN static assets directory
│   ├── app.js
│   ├── index.css
│   └── index.html
├── marketmind.db                     # Pre-seeded SQLite production database
├── marketmind_default.db             # Clean baseline backup for "Restore Demo" action
├── requirements.txt                  # Python production dependencies for Vercel
├── vercel.json                       # Vercel deployment routes & serverless configuration
├── .vercelignore                     # Vercel deployment exclusion rules
├── .gitignore                        # Git repository ignore rules
└── README.md                         # This deployment and user guide
```

---

## 🚀 How to Deploy to Vercel via GitHub

Deploying MarketMind AI to Vercel takes under 3 minutes using standard GitHub integration:

### Step 1: Extract or Prepare the Milestone 4 Code
1. Use the pre-packaged **`Milestone_4.zip`** or the contents of this `Milestone_4` directory.
2. Initialize a Git repository if pushing to a new repo:
   ```bash
   git init
   git add .
   git commit -m "feat(milestone4): MarketMind AI complete web application production release"
   ```

### Step 2: Push to GitHub
1. Create a new repository on your GitHub account (e.g., `marketmind-ai-platform`).
2. Push your code:
   ```bash
   git remote add origin https://github.com/<YOUR_USERNAME>/marketmind-ai-platform.git
   git branch -M main
   git push -u origin main
   ```

### Step 3: Connect and Deploy on Vercel
1. Log in to [Vercel](https://vercel.com).
2. Click **"Add New..."** → **"Project"**.
3. Select your GitHub repository (`marketmind-ai-platform`) and click **"Import"**.
4. Configure the project settings:
   - **Framework Preset:** `Other`
   - **Root Directory:** `./` (leave default)
   - **Build Command:** Leave empty (Vercel automatically detects Python serverless runtime)
   - **Output Directory:** Leave empty
5. Click **"Deploy"**.
6. Within ~60 seconds, Vercel will build the serverless functions, deploy static assets to the global Edge CDN, and provide your live production URL (e.g., `https://marketmind-ai.vercel.app`).

---

## 🔐 Default Demonstration Accounts

You can log in directly using one of the pre-configured role accounts (or use the one-click demo role selector buttons on the login screen):

| Role | Email Address | Password | Primary Capabilities |
| :--- | :--- | :--- | :--- |
| **Business Owner** | `owner@marketmind.ai` | `OwnerPass123!` | Executive revenue KPIs, forecasts, model selector, strategic insights |
| **Store Manager** | `manager@marketmind.ai` | `ManagerPass123!` | Category sales, inventory anomalies, reorder triggers, operational insights |
| **Sales Executive** | `sales@marketmind.ai` | `SalesPass123!` | Customer directory, churn risk alerts, personalized product cross-sells |
| **Administrator** | `admin@marketmind.ai` | `AdminPass123!` | System health, model telemetry, universal dataset upload & reset tools |

---

## 💻 Running Locally

To test the complete web application locally on your computer:

1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Launch Application:**
   ```bash
   uvicorn backend.main:app --host 127.0.0.1 --port 8080 --reload
   ```

3. **Access in Browser:**
   - Web Application Dashboard: [http://127.0.0.1:8080](http://127.0.0.1:8080)
   - Interactive Swagger API Documentation: [http://127.0.0.1:8080/docs](http://127.0.0.1:8080/docs)
   - ReDoc API Reference: [http://127.0.0.1:8080/redoc](http://127.0.0.1:8080/redoc)
   - Health Status Endpoint: [http://127.0.0.1:8080/health](http://127.0.0.1:8080/health)

---

## 🛡️ Vercel Serverless Architecture Details

- **Read-Only Filesystem Adaptation:** Vercel functions execute in a read-only environment except for `/tmp`. MarketMind AI automatically initializes `/tmp/marketmind.db` on first spin-up so live dataset uploads and demo restorations run without file permission conflicts.
- **Dual-Mount URL Routing:** All API endpoints are dual-mounted under both `/api/*` and `/*` in FastAPI, ensuring 100% route resolution regardless of Vercel rewrites or proxy conventions.
- **Edge CDN Optimization:** Static HTML, CSS, and JS assets are mirrored in `public/`, `frontend/`, and project root to guarantee immediate global cache hit ratios.
