# MarketMind AI — Conversation 1 Summary & Milestone 1 Record

This document serves as the permanent record of **Conversation 1 (Milestone 1)** for MarketMind AI.

## 📌 Project Overview
**MarketMind AI — Small Business Sales Intelligence Platform (Milestone 1)**
- **GitHub Repository**: [springboardmentor160-debug/AI-Powered-Small-Business-Sales-Forecasting-and-Revenue-Growth-Intelligence-Platform](https://github.com/springboardmentor160-debug/AI-Powered-Small-Business-Sales-Forecasting-and-Revenue-Growth-Intelligence-Platform)
- **Local Directory**: `D:/Infosys`

---

## 🎯 Summary of Completed Milestone 1 Stages

### Stage 1: Data & Objectives
- **Raw POS Dataset**: Generated 350+ realistic retail transaction records with fields: `transaction_id, date, product_id, product_name, category, quantity, unit_price, total_amount, store_id, customer_id, payment_method, stock_level, reorder_threshold`.
- **Data Dictionary**: Created [data_dictionary.md](file:///D:/Infosys/docs/data_dictionary.md) explaining all columns and cleaning rules.
- **Project Objectives**: Created [objectives.md](file:///D:/Infosys/docs/objectives.md) covering problem statement, 4 target user personas, and Mermaid data flow diagram.

### Stage 2: Design
- **Architecture**: Created [architecture.md](file:///D:/Infosys/docs/architecture.md) detailing decoupled FastAPI + React + SQLite architecture with Mermaid sequence and component diagrams.
- **DB Schema**: Created [db_schema.md](file:///D:/Infosys/docs/db_schema.md) and SQL DDL file [schema.sql](file:///D:/Infosys/db/schema.sql) with tables `users`, `roles`, `transactions`, `inventory`, `customers`, `stores`.
- **Wireframes**: Created [wireframes.md](file:///D:/Infosys/docs/wireframes.md) with ASCII layouts for login page and the 4 role dashboards.

### Stage 3: Data Prep
- **ETL Scripts**: Created `generate_raw_data.py`, `clean_data.py`, and `load_db.py` in `/backend/data_prep`.
- **Relational Storage**: Populated SQLite database at `db/marketmind.db`.

### Stage 4: Initial Build
- **FastAPI Backend**: Routers implemented for `/api/v1/analytics/summary`, `/api/v1/sales`, and `/api/v1/inventory`.
- **React Frontend**: Built dark-mode SPA with Vite, Recharts, and custom CSS design system (`index.css`).

### Stage 5: Access Control (JWT & RBAC)
- **JWT Hashing & Authentication**: Endpoints `POST /api/v1/auth/login`, `POST /api/v1/auth/register`, `GET /api/v1/auth/me`.
- **Role-Based Access Control (RBAC)**: Configured 4 default roles with store isolation and admin user management panel.
- **Frontend Login Portal**: Sleek login modal with quick demo shortcuts (`owner`, `manager`, `exec`, `admin`).

---

## 🔑 Demo Login Accounts

| Role | Username | Password | Permission Scope |
| :--- | :--- | :--- | :--- |
| **Business Owner** | `owner` | `password123` | Executive global metrics across all stores. |
| **Store Manager** | `manager` | `password123` | Enforced store scope (`STORE-001`), stock alerts & inventory management. |
| **Sales Executive** | `exec` | `password123` | Terminal sales history, quick product lookup. |
| **Administrator** | `admin` | `password123` | User administration (`/api/v1/users`), RBAC provisioning, system audit logs. |

---

## 🛠️ How to Run
```bash
# 1. Seed Database
python backend/data_prep/generate_raw_data.py
python backend/data_prep/clean_data.py
python backend/data_prep/load_db.py

# 2. Run Backend
cd backend
python -m uvicorn main:app --reload --port 8000

# 3. Run Frontend
cd frontend
npm run dev
```
