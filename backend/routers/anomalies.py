import logging
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query

from backend.auth import require_role
from backend.services.ml_service import get_anomaly_overview

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/anomalies",
    tags=["Anomaly Detection"],
)

ALLOWED_ROLES = ["business_owner", "admin", "store_manager"]


@router.get("")
def anomaly_alerts(
    alert_type: Literal[
        "unusual_sales_activity", "stock_write_off", "demand_spike"
    ] | None = None,
    severity: Literal["high", "medium"] | None = None,
    limit: int = Query(default=50, ge=1, le=500),
    user: dict = Depends(require_role(ALLOWED_ROLES)),
):
    logger.info("Anomaly alerts requested by %s", user["sub"])

    try:
        result = get_anomaly_overview(
            top_n=limit,
            alert_type=alert_type,
            severity=severity,
        )
    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except Exception as error:
        logger.exception("Anomaly alerts failed.")
        raise HTTPException(
            status_code=500,
            detail=f"Unable to load anomaly alerts: {error}",
        ) from error

    return {
        "status": "Access Granted",
        "feature": "Anomaly Detection",
        **result,
    }
