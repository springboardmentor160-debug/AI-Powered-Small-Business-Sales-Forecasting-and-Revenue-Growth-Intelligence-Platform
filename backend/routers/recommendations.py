import logging

from fastapi import APIRouter, Depends, HTTPException, Query

from backend.auth import require_role
from backend.services.ml_service import (
    get_customer_recommendations,
    get_full_recommendations,
    get_product_recommendations,
    get_recommendation_overview,
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/recommendations",
    tags=["Recommendations"],
)

ALLOWED_ROLES = [
    "business_owner",
    "admin",
    "store_manager",
    "sales_executive",
]


def _run(action, description: str):
    try:
        return action()
    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except Exception as error:
        logger.exception("%s failed.", description)
        raise HTTPException(
            status_code=500,
            detail=f"Unable to load {description}: {error}",
        ) from error


@router.get("/overview")
def recommendation_overview(
    user: dict = Depends(require_role(ALLOWED_ROLES)),
):
    result = _run(get_recommendation_overview, "recommendation overview")
    return {
        "status": "Access Granted",
        "feature": "Product Recommendation Engine",
        **result,
    }


@router.get("/customer/{customer_id}")
def customer_recommendations(
    customer_id: int,
    stock_code: str | None = Query(
        default=None,
        description="Product being viewed/bought, adds cross-sell and upsell.",
    ),
    user: dict = Depends(require_role(ALLOWED_ROLES)),
):
    logger.info(
        "Recommendations for customer %s requested by %s",
        customer_id,
        user["sub"],
    )
    result = _run(
        lambda: get_full_recommendations(customer_id, stock_code),
        "customer recommendations",
    )
    return {"status": "Access Granted", "customer_id": customer_id, **result}


@router.get("/product/{stock_code}")
def product_recommendations(
    stock_code: str,
    user: dict = Depends(require_role(ALLOWED_ROLES)),
):
    result = _run(
        lambda: get_product_recommendations(stock_code),
        "product recommendations",
    )
    if not result["frequently_bought_with"] and not result["upsell_opportunities"]:
        raise HTTPException(
            status_code=404,
            detail=f"No recommendations found for product {stock_code}.",
        )
    return {"status": "Access Granted", **result}
