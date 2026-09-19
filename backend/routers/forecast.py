import os
import json
import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any, List

from auth import require_role
import models

router = APIRouter(tags=["Sales Forecasting"])

# Per the Access Matrix: Business Owner: YES, Store Manager: VIEW, Admin: YES, Sales Executive: NO (403)
forecast_authorized = require_role(["business_owner", "store_manager", "administrator", "admin"])

def get_artifacts_dir() -> str:
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    return os.path.join(base_dir, "artifacts")

@router.get("/forecast/revenue", dependencies=[Depends(forecast_authorized)])
@router.get("/api/v1/forecast/revenue", dependencies=[Depends(forecast_authorized)])
def get_revenue_forecast() -> Dict[str, Any]:
    """
    Returns the 30-day ahead total revenue forecast and performance metrics
    from the winning model.
    Access Matrix: Business Owner, Store Manager, Admin only. Sales Executive receives 403.
    """
    artifacts_dir = get_artifacts_dir()
    summary_path = os.path.join(artifacts_dir, "forecast_summary.json")

    if not os.path.exists(summary_path):
        from backend.ml.train import train_all_artifacts
        train_all_artifacts()

    with open(summary_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    return {
        "period": data["period"],
        "predicted_revenue": data["predicted_revenue"],
        "model_used": data["model_used"],
        "metrics": data["metrics"],
        "missing_dates_count": data.get("missing_dates_count", 0),
        "daily_count": len(data.get("daily_forecast", []))
    }

@router.get("/forecast/series", dependencies=[Depends(forecast_authorized)])
@router.get("/api/v1/forecast/series", dependencies=[Depends(forecast_authorized)])
def get_forecast_series() -> Dict[str, Any]:
    """
    Returns the complete historical daily sales timeline combined with the
    30-day forecasted series and upper/lower confidence bounds.
    """
    artifacts_dir = get_artifacts_dir()
    summary_path = os.path.join(artifacts_dir, "forecast_summary.json")

    if not os.path.exists(summary_path):
        from backend.ml.train import train_all_artifacts
        train_all_artifacts()

    with open(summary_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Load historical daily series
    from backend.ml.forecasting import prepare_daily_revenue
    daily_revenue, _, _ = prepare_daily_revenue()
    historical = [
        {"date": row["date"].strftime("%Y-%m-%d"), "revenue": round(float(row["revenue"]), 2)}
        for _, row in daily_revenue.iterrows()
    ]

    return {
        "historical": historical,
        "forecast": data["daily_forecast"],
        "model_used": data["model_used"]
    }
