from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
from backend.models import User
from backend.dependencies import get_current_user, require_roles
from backend.forecasting.pipeline import run_forecasting_pipeline

router = APIRouter(prefix="/api/v1/forecasting", tags=["Sales Forecasting"])


@router.get("/summary", response_model=Dict[str, Any])
def get_forecasting_summary(
    current_user: User = Depends(require_roles(["owner", "manager", "admin"]))
):
    """
    Get 30-day Prophet Sales Forecast summary including missing-date check and uncertainty bounds.
    Protected endpoint: Owner, Manager, Admin only.
    """
    try:
        _, summary = run_forecasting_pipeline()
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate sales forecast: {str(e)}")
