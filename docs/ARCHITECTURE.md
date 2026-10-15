# Architecture

```
React/Vite dashboard (localhost:5173) --/api proxy--> FastAPI (localhost:8000)
                                                        |-- SQLite  data/marketmind.db   users, roles, invoices, sales_transactions,
                                                        |                                 products, customers, transactions
                                                        '-- ml/outputs/*.json|csv|png|xlsx   results written by the ML scripts
datasets/raw -> data_cleaning*.py -> datasets/processed/*.csv -> load_data.py -> SQLite
                                                              '-> ml/*.py -> ml/outputs
```

* **Live data** (sales KPIs, trends, inventory, invoices, users) is queried from SQLite with SQLAlchemy on each request.
* **AI results** (segments, forecast, recommendations, churn, anomalies, model evaluation, Excel report) are produced offline by `ml/run_all.py` and served from `ml/outputs`; an endpoint returns 503 with a clear message if its file has not been generated. Nothing is hard-coded in the API.
* **Auth:** `/login` returns a JWT (HS256, `SECRET_KEY`). Every protected route validates the token, re-reads the user from the database and checks the role against the `ACCESS` matrix in `backend/auth.py` (401 invalid/expired/deleted user, 403 wrong role).
* **Vite proxy:** the frontend calls `/api/...`; `vite.config.js` forwards it to port 8000 and strips `/api`, so no CORS is needed in development. CORS origins for direct calls are in `CORS_ORIGINS`.
* **Why not Spring Boot?** The uploaded project is a complete FastAPI application and the official milestone text was not provided, so no second backend was added. If a Spring Boot service is mandatory it would sit beside this one (calling these REST endpoints or reading the same SQLite file) rather than replace the Python ML layer; JWT secret/algorithm would have to be shared if it should accept the same tokens.
