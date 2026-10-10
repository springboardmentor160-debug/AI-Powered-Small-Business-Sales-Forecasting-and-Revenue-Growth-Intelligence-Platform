# MarketMind AI — Small Business Sales Intelligence Platform

Milestone 1 implementation for the Infosys Springboard project.

## Stack

- Backend: Python + FastAPI
- Frontend: React + Vite
- Database: SQLite
- Data: Pandas + NumPy
- Authentication: JWT
- Authorization: Role-Based Access Control

## Milestone 1 Features

- Retail sales, customer, product and inventory datasets
- Data exploration
- Data cleaning and preprocessing
- SQLite database
- FastAPI backend
- React dashboard
- JWT login
- Four user roles
- Role-based API permissions
- Sales summary
- Sales trend
- Top products
- Inventory alerts
- Basic transaction/invoice management
- CSV sales upload endpoint

## Roles

- Business Owner
- Store Manager
- Sales Executive
- Administrator

## Demo Login

| Role | Email | Password |
|---|---|---|
| Business Owner | owner@marketmind.ai | owner123 |
| Store Manager | manager@marketmind.ai | manager123 |
| Sales Executive | sales@marketmind.ai | sales123 |
| Administrator | admin@marketmind.ai | admin123 |

These are local demo credentials only. Change them before any real deployment.

## Run Backend

```bash
cd backend
python -m venv venv
```

Windows:

```bash
venv\Scripts\activate
```

Install:

```bash
pip install -r requirements.txt
```

Copy `.env.example` to `.env`.

Run:

```bash
uvicorn app.main:app --reload --port 8000
```

API:
http://127.0.0.1:8000

Swagger:
http://127.0.0.1:8000/docs

## Run Frontend

Open a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open the Vite URL shown in the terminal, normally:

```text
http://localhost:5173
```

## Regenerate datasets

From the project root:

```bash
python generate_data.py
python clean_data.py
python explore_data.py
```

## Project Flow

Raw CSV
→ Exploration
→ Cleaning
→ SQLite
→ FastAPI
→ React Dashboard
→ Authentication/RBAC

## Important

Do not commit `.env`, `backend/marketmind.db`, `backend/venv`, or real credentials to GitHub.
