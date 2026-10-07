from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Dict, Any, List, Optional
from backend.models import User
from backend.dependencies import require_roles
from backend.churn.pipeline import run_churn_pipeline

router = APIRouter(prefix="/api/v1/churn", tags=["Customer Churn Intelligence"])


@router.get("", response_model=Dict[str, Any])
def get_churn_intelligence_summary(
    inactivity_days: int = Query(default=2, ge=1, le=30),
    high_threshold: float = Query(default=0.7, ge=0.5, le=1.0),
    medium_threshold: float = Query(default=0.4, ge=0.1, le=0.7),
    current_user: User = Depends(require_roles(["owner", "manager", "admin"]))
):
    """
    Get customer churn intelligence overview:
    - Multi-model evaluation (Logistic Regression, Random Forest, XGBoost)
    - Precision, Recall, F1-score, and Accuracy
    - Selected model with business rationale
    - Full customer cohort probabilities and High/Medium/Low retention risk classifications
    - Churn risk distribution across Milestone 2 segments.
    Protected endpoint: Owner, Manager, Admin only.
    """
    try:
        inactivity_val = inactivity_days if isinstance(inactivity_days, int) else 2
        high_val = high_threshold if isinstance(high_threshold, (int, float)) else 0.7
        med_val = medium_threshold if isinstance(medium_threshold, (int, float)) else 0.4

        _, summary = run_churn_pipeline(
            inactivity_threshold=inactivity_val,
            high_risk_threshold=high_val,
            medium_risk_threshold=med_val
        )
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate churn intelligence: {str(e)}")


@router.get("/{customer_id}", response_model=Dict[str, Any])
def get_single_customer_churn_risk(
    customer_id: str,
    inactivity_days: int = Query(default=2, ge=1, le=30),
    high_threshold: float = Query(default=0.7, ge=0.5, le=1.0),
    medium_threshold: float = Query(default=0.4, ge=0.1, le=0.7),
    current_user: User = Depends(require_roles(["owner", "manager", "admin"]))
):
    """
    Get churn probability and retention risk for a specific customer.
    Protected endpoint: Owner, Manager, Admin only.
    """
    try:
        inactivity_val = inactivity_days if isinstance(inactivity_days, int) else 2
        high_val = high_threshold if isinstance(high_threshold, (int, float)) else 0.7
        med_val = medium_threshold if isinstance(medium_threshold, (int, float)) else 0.4

        _, summary = run_churn_pipeline(
            inactivity_threshold=inactivity_val,
            high_risk_threshold=high_val,
            medium_risk_threshold=med_val
        )
        cohort = summary.get("customer_cohort", [])
        matched = next((c for c in cohort if c["customer_id"] == customer_id), None)
        if not matched:
            raise HTTPException(status_code=404, detail=f"Customer '{customer_id}' not found in churn cohort.")

        return {
            "customer": matched,
            "selected_model": summary.get("selected_model"),
            "risk_thresholds": summary.get("risk_thresholds")
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve customer churn record: {str(e)}")
