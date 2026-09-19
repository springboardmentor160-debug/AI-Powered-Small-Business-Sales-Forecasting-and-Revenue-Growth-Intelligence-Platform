import os
import json
import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Dict, Any, List, Optional

from auth import require_role
from backend.ml.forecasting import prepare_daily_revenue, evaluate_models, run_recursive_forecast
import models

router = APIRouter(tags=["Sales Forecasting"])

# Per the Access Matrix: Business Owner: YES, Store Manager: VIEW, Admin: YES, Sales Executive: NO (403)
forecast_authorized = require_role(["business_owner", "store_manager", "administrator", "admin"])

def get_artifacts_dir() -> str:
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    return os.path.join(base_dir, "artifacts")

@router.get("/forecast/revenue", dependencies=[Depends(forecast_authorized)])
@router.get("/api/v1/forecast/revenue", dependencies=[Depends(forecast_authorized)])
def get_revenue_forecast(
    periods: int = Query(30, ge=7, le=180, description="Forecast horizon in days"),
    model: Optional[str] = Query(None, description="Model: Prophet, Random Forest Regressor, XGBoost Regressor"),
    store_id: Optional[str] = Query(None, description="Optional store filter"),
    force_recompute: bool = Query(False, description="Force dynamic recomputation from live database")
) -> Dict[str, Any]:
    """
    Returns the total revenue forecast and performance metrics.
    Supports dynamic horizon (7, 14, 30, 60, 90 days), model selection, and live database queries.
    Access Matrix: Business Owner, Store Manager, Admin only. Sales Executive receives 403.
    """
    artifacts_dir = get_artifacts_dir()
    summary_path = os.path.join(artifacts_dir, "forecast_summary.json")

    # Fast path for default 30-day global horizon if cached
    if periods == 30 and model is None and store_id is None and not force_recompute and os.path.exists(summary_path):
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

    # Dynamic execution on live database data
    daily_revenue, missing_cnt, missing_dates = prepare_daily_revenue(store_id=store_id)
    eval_res = evaluate_models(daily_revenue, artifacts_dir=artifacts_dir)
    forecast_res = run_recursive_forecast(daily_revenue, eval_res, periods=periods, selected_model=model)

    return {
        "period": forecast_res["period"],
        "predicted_revenue": forecast_res["predicted_revenue"],
        "model_used": forecast_res["model_used"],
        "metrics": forecast_res["metrics"],
        "missing_dates_count": missing_cnt,
        "daily_count": len(forecast_res["daily_forecast"])
    }

@router.get("/forecast/series", dependencies=[Depends(forecast_authorized)])
@router.get("/api/v1/forecast/series", dependencies=[Depends(forecast_authorized)])
def get_forecast_series(
    periods: int = Query(30, ge=7, le=180, description="Forecast horizon in days"),
    model: Optional[str] = Query(None, description="Model: Prophet, Random Forest Regressor, XGBoost Regressor"),
    store_id: Optional[str] = Query(None, description="Optional store filter"),
    force_recompute: bool = Query(False, description="Force dynamic recomputation from live database")
) -> Dict[str, Any]:
    """
    Returns complete historical daily timeline, dynamic multi-day forecast with confidence bounds,
    and side-by-side test window predictions for all 3 models.
    """
    artifacts_dir = get_artifacts_dir()
    summary_path = os.path.join(artifacts_dir, "forecast_summary.json")

    # Fast path for default 30-day global horizon if cached
    if periods == 30 and model is None and store_id is None and not force_recompute and os.path.exists(summary_path):
        with open(summary_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        daily_revenue, _, _ = prepare_daily_revenue()
        historical = [
            {"date": row["date"].strftime("%Y-%m-%d"), "revenue": round(float(row["revenue"]), 2)}
            for _, row in daily_revenue.iterrows()
        ]
        return {
            "historical": historical,
            "forecast": data["daily_forecast"],
            "model_used": data["model_used"],
            "test_evaluation_series": data.get("test_evaluation_series", {}),
            "metrics": data.get("metrics", {})
        }

    # Dynamic execution on live database data
    daily_revenue, _, _ = prepare_daily_revenue(store_id=store_id)
    eval_res = evaluate_models(daily_revenue, artifacts_dir=artifacts_dir)
    forecast_res = run_recursive_forecast(daily_revenue, eval_res, periods=periods, selected_model=model)

    historical = [
        {"date": row["date"].strftime("%Y-%m-%d"), "revenue": round(float(row["revenue"]), 2)}
        for _, row in daily_revenue.iterrows()
    ]

    return {
        "historical": historical,
        "forecast": forecast_res["daily_forecast"],
        "model_used": forecast_res["model_used"],
        "test_evaluation_series": eval_res.get("test_evaluation_series", {}),
        "metrics": eval_res["metrics"]
    }

@router.post("/forecast/recompute", dependencies=[Depends(forecast_authorized)])
@router.post("/api/v1/ml/refresh", dependencies=[Depends(forecast_authorized)])
def trigger_ml_refresh():
    """
    Triggers full recomputation of ML models on live database records and updates artifacts.
    """
    from backend.ml.train import train_all_artifacts
    results = train_all_artifacts()
    return {
        "status": "success",
        "message": "All ML models and business reports successfully refreshed with latest database records.",
        "winner_model": results["forecasting"]["model_used"],
        "projected_revenue": results["forecasting"]["predicted_revenue"]
    }
