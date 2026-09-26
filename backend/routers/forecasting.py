import os
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from typing import Dict, Any, List
from backend.models import User
from backend.dependencies import get_current_user, require_roles
from backend.forecasting.pipeline import (
    run_forecasting_pipeline,
    BUSINESS_REPORT_PATH
)

router = APIRouter(prefix="/api/v1/forecasting", tags=["Sales Forecasting"])


@router.get("/summary", response_model=Dict[str, Any])
def get_forecasting_summary(
    current_user: User = Depends(require_roles(["owner", "manager", "admin"]))
):
    """
    Get 30-day multi-model sales forecast summary including missing-date check,
    model comparison (Prophet vs RF vs XGBoost), and uncertainty bounds.
    Protected endpoint: Owner, Manager, Admin only.
    """
    try:
        _, summary = run_forecasting_pipeline()
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate sales forecast: {str(e)}")


@router.get("/revenue", response_model=Dict[str, Any])
def get_forecast_revenue(
    current_user: User = Depends(require_roles(["owner", "manager", "admin"]))
):
    """
    Get revenue forecast for the next 30 days using the model selected based on lowest evaluation error.
    Protected endpoint: Owner, Manager, Admin only.
    """
    try:
        _, summary = run_forecasting_pipeline()
        return {
            "period": summary.get("period", "Next 30 Days"),
            "predicted_revenue": summary.get("predicted_revenue", 0.0),
            "model_used": summary.get("model_used", "Prophet"),
            "selection_reason": summary.get("selection_reason", ""),
            "historical_period": summary.get("historical_period", {})
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve revenue forecast: {str(e)}")


@router.get("/models", response_model=List[Dict[str, Any]])
def get_forecast_models_comparison(
    current_user: User = Depends(require_roles(["owner", "manager", "admin"]))
):
    """
    Get real multi-model comparison table (Prophet, Random Forest, XGBoost) with MAE and RMSE.
    Protected endpoint: Owner, Manager, Admin only.
    """
    try:
        _, summary = run_forecasting_pipeline()
        return summary.get("model_comparison", [])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve model comparison: {str(e)}")


@router.get("/report")
def download_business_report(
    current_user: User = Depends(require_roles(["owner", "manager", "admin"]))
):
    """
    Download the generated Excel business report (Customer Segments, Sales Forecast, Model Comparison).
    Protected endpoint: Owner, Manager, Admin only.
    """
    try:
        if not os.path.exists(BUSINESS_REPORT_PATH):
            run_forecasting_pipeline()

        if not os.path.exists(BUSINESS_REPORT_PATH):
            raise HTTPException(status_code=404, detail="Business report file not found.")

        return FileResponse(
            BUSINESS_REPORT_PATH,
            filename="business_report.xlsx",
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to download business report: {str(e)}")
