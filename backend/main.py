"""
FastAPI Backend Application Entrypoint for Milestone 4 (MarketMind AI)
Unified Enterprise Sales Forecasting, RFM Segmentation, Recommendations,
Churn Prediction, Anomaly Detection, and Real-Time Dataset Ingestion.
"""

import os
import json
import pandas as pd
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

from .routes import router as api_router
from .database import SessionLocal, DB_PATH, ensure_db_initialized
from .db_service import init_db_tables, seed_demo_users, populate_milestone3_results
from .db_models import User

app = FastAPI(
    title="MarketMind AI - Milestone 4 Enterprise Sales Intelligence Platform",
    version="4.0.0",
    description="Backend API serving Product Recommendations, Customer Churn Prediction, Anomaly/Fraud Detection, Sales Forecasting, and RFM Segmentation."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi import Request
import traceback

@app.middleware("http")
async def error_handling_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as exc:
        tb = traceback.format_exc()
        print(f"[FATAL SERVER EXCEPTION] {exc}\n{tb}")
        return JSONResponse(
            status_code=500,
            content={
                "detail": f"Internal Server Error: {str(exc)}",
                "error_type": type(exc).__name__,
                "traceback": tb.split("\n")
            }
        )

def init_app_database():
    """Ensure database schema is created and populated safely."""
    try:
        ensure_db_initialized()
    except Exception as e:
        print(f"[DB Init Warning] {e}")

@app.on_event("startup")
def on_startup():
    init_app_database()

# Health check endpoints for Vercel, Docker, CI/CD, and monitoring
@app.get("/health", tags=["System"])
@app.get("/api/health", tags=["System"])
def health_check():
    ensure_db_initialized()
    db_exists = os.path.exists(DB_PATH)
    db_size = os.path.getsize(DB_PATH) if db_exists else 0
    users_count = 0
    try:
        db = SessionLocal()
        users_count = db.query(User).count()
        db.close()
    except Exception as e:
        users_count = f"Error: {e}"
        
    return {
        "status": "healthy",
        "service": "MarketMind AI Enterprise Platform",
        "version": "4.0.0",
        "database": os.path.basename(DB_PATH),
        "db_path": DB_PATH,
        "db_exists": db_exists,
        "db_size": db_size,
        "users_count": users_count
    }

# Mount API router under both /api and root to guarantee routing across all deployment configurations
app.include_router(api_router, prefix="/api")
app.include_router(api_router)

# Locate frontend static assets (checks public/, frontend/, then root)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
STATIC_DIR = os.path.join(BASE_DIR, "public")
if not os.path.exists(STATIC_DIR):
    STATIC_DIR = os.path.join(BASE_DIR, "frontend")
if not os.path.exists(STATIC_DIR):
    STATIC_DIR = BASE_DIR

if os.path.exists(STATIC_DIR):
    index_file = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_file):
        @app.get("/", include_in_schema=False)
        def read_root():
            return FileResponse(index_file)

    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
    app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="frontend_root")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8080, reload=True)

