"""
FastAPI Backend Application Entrypoint for Milestone 3 (MarketMind AI)
Includes Product Recommendations, Churn Prediction, and Anomaly Detection.
"""

import os
import json
import pandas as pd
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from .routes import router as api_router
from .database import SessionLocal
from .db_service import init_db_tables, seed_demo_users, populate_milestone3_results

app = FastAPI(
    title="MarketMind AI - Milestone 3 Enterprise Sales Intelligence Platform",
    version="3.0.0",
    description="Backend API serving Product Recommendations, Customer Churn Prediction, Anomaly/Fraud Detection, Sales Forecasting, and RFM Segmentation."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def init_app_database():
    """Ensure database schema is created and populated with demo accounts and Milestone 3 outputs."""
    try:
        init_db_tables()
        db = SessionLocal()
        seed_demo_users(db)
        
        outputs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "outputs"))
        populate_milestone3_results(db, outputs_dir)
        db.close()
    except Exception as e:
        print(f"[Startup Warning] Could not initialize database on startup: {e}")

# Run DB init on startup
init_app_database()

@app.on_event("startup")
def on_startup():
    init_app_database()

# Mount API router
app.include_router(api_router)

# Mount static frontend directory
FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))

if os.path.exists(FRONTEND_DIR):
    @app.get("/", include_in_schema=False)
    def read_root():
        index_file = os.path.join(FRONTEND_DIR, "index.html")
        if os.path.exists(index_file):
            return FileResponse(index_file)
        return {"message": "MarketMind AI Milestone 3 Backend API is running."}

    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend_root")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("Milestone_3.backend.main:app", host="127.0.0.1", port=8080, reload=True)
