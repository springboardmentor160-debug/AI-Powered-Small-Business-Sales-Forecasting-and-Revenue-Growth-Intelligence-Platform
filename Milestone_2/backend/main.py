"""
FastAPI Backend Application Entrypoint for Milestone 2 (MarketMind AI)
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
from .db_service import init_db_tables, seed_database_from_sources, save_segmentation_results_to_db, save_forecasting_results_to_db

app = FastAPI(
    title="MarketMind AI - Milestone 2 Sales Forecasting & Customer Intelligence API",
    version="2.0.0",
    description="Backend API serving empirical customer segmentation, time-series sales/revenue forecasting, model metrics, and business reports."
)

# Enable CORS for local dashboard development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def init_app_database():
    """Ensure database schema is created and populated."""
    try:
        init_db_tables()
        db = SessionLocal()
        source_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "source"))
        seed_database_from_sources(db, source_dir)
        
        outputs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "outputs"))
        seg_csv = os.path.join(outputs_dir, "segmentation", "customer_segments.csv")
        sum_csv = os.path.join(outputs_dir, "segmentation", "cluster_summary.csv")
        seg_json = os.path.join(outputs_dir, "segmentation", "segmentation_metrics.json")
        
        if os.path.exists(seg_csv) and os.path.exists(sum_csv) and os.path.exists(seg_json):
            df_feat = pd.read_csv(seg_csv)
            df_prof = pd.read_csv(sum_csv, index_col=0)
            metrics = json.load(open(seg_json, "r", encoding="utf-8"))
            save_segmentation_results_to_db(df_feat, df_prof, metrics, db)

        fcst_comb = os.path.join(outputs_dir, "forecasting", "combined_forecasts.csv")
        fcst_json = os.path.join(outputs_dir, "forecasting", "model_metrics.json")

        if os.path.exists(fcst_comb) and os.path.exists(fcst_json):
            df_comb = pd.read_csv(fcst_comb)
            metrics_fcst = json.load(open(fcst_json, "r", encoding="utf-8"))
            best_m = metrics_fcst.get("best_performing_model", "Prophet")
            save_forecasting_results_to_db(df_comb, metrics_fcst["model_metrics"], best_m, db)

        db.close()
    except Exception as e:
        print(f"[Startup Warning] Could not seed database on startup: {e}")

# Run DB init on app load
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
        return {"message": "MarketMind AI Milestone 2 Backend API is running."}

    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend_root")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("Milestone_2.backend.main:app", host="127.0.0.1", port=8000, reload=True)
