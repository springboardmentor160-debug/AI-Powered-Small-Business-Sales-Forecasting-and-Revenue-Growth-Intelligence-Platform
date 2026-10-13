import logging

from fastapi import APIRouter, Depends, HTTPException, Query

from backend.auth import require_role
from backend.services.ml_service import (
    RISK_LEVELS,
    get_churn_overview,
    get_customer_churn,
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/churn",
    tags=["Churn Prediction"],
)

ALLOWED_ROLES = ["business_owner", "admin", "store_manager"]


@router.get("")
def churn_overview(
    risk: str | None = Query(
        default=None,
        description="Filter customers: High Risk, Medium Risk or Low Risk.",
    ),
    limit: int = Query(default=25, ge=1, le=500),
    active_only: bool = Query(
        default=False,
        description="Only customers who bought in the last 90 days.",
    ),
    user: dict = Depends(require_role(ALLOWED_ROLES)),
):
    if risk is not None and risk not in RISK_LEVELS:
        raise HTTPException(
            status_code=422,
            detail=f"risk must be one of {list(RISK_LEVELS)}",
        )

    logger.info("Churn overview requested by %s", user["sub"])

    try:
        result = get_churn_overview(
            top_n=limit,
            risk=risk,
            active_only=active_only,
        )
    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except Exception as error:
        logger.exception("Churn overview failed.")
        raise HTTPException(
            status_code=500,
            detail=f"Unable to load churn predictions: {error}",
        ) from error

    return {
        "status": "Access Granted",
        "feature": "Churn Prediction",
        **result,
    }


@router.get("/customer/{customer_id}")
def customer_churn(
    customer_id: int,
    user: dict = Depends(require_role(ALLOWED_ROLES)),
):
    try:
        result = get_customer_churn(customer_id)
    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error

    if result is None:
        raise HTTPException(
            status_code=404,
            detail=f"Customer {customer_id} has no churn prediction.",
        )

    return {"status": "Access Granted", "customer": result}
