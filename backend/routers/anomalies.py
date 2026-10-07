from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Dict, Any, List
from backend.models import User
from backend.dependencies import require_roles
from backend.anomalies.pipeline import run_anomaly_pipeline

router = APIRouter(prefix="/api/v1/anomalies", tags=["Anomaly Detection"])


@router.get("", response_model=Dict[str, Any])
def get_anomalies_full(
    z_threshold: float = Query(default=3.0, ge=1.0, le=5.0),
    contamination: float = Query(default=0.02, ge=0.01, le=0.5),
    current_user: User = Depends(require_roles(["owner", "manager", "admin"]))
):
    """
    Get comprehensive anomaly detection report:
    - Statistical Z-Score (1D) vs Isolation Forest (3D) comparison
    - Detected anomalous transactions
    - Actionable human-review alerts
    - Inventory audit readiness assessment.
    Protected endpoint: Owner, Manager, Admin only.
    """
    try:
        z_val = z_threshold if isinstance(z_threshold, (int, float)) else 3.0
        contam_val = contamination if isinstance(contamination, (int, float)) else 0.02
        _, summary = run_anomaly_pipeline(z_threshold=z_val, contamination=contam_val)
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to run anomaly detection: {str(e)}")


@router.get("/summary", response_model=Dict[str, Any])
def get_anomalies_summary(
    z_threshold: float = Query(default=3.0, ge=1.0, le=5.0),
    contamination: float = Query(default=0.02, ge=0.01, le=0.5),
    current_user: User = Depends(require_roles(["owner", "manager", "admin"]))
):
    """
    Get lightweight summary of detected anomalies and review alerts.
    Protected endpoint: Owner, Manager, Admin only.
    """
    try:
        z_val = z_threshold if isinstance(z_threshold, (int, float)) else 3.0
        contam_val = contamination if isinstance(contamination, (int, float)) else 0.02
        _, summary = run_anomaly_pipeline(z_threshold=z_val, contamination=contam_val)
        return {
            "total_transactions": summary.get("total_transactions_analyzed", 0),
            "anomalies_detected_count": summary.get("anomalies_detected_count", 0),
            "comparison": summary.get("comparison", {}),
            "alerts": summary.get("alerts", []),
            "inventory_support": summary.get("inventory_anomalies", {})
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve anomaly summary: {str(e)}")
