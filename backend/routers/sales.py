import logging

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.auth import require_role
from backend.database import get_db
from backend.models.product import Product
from backend.models.sale import Sale


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/sales",
    tags=["Sales"],
)


@router.get("/summary")
def sales_summary(
    db: Session = Depends(get_db),
    user: dict = Depends(
        require_role(["business_owner", "admin"])
    ),
):
    logger.info(
        "Sales summary requested by %s",
        user["sub"],
    )

    total_revenue = db.scalar(
        select(
            func.coalesce(
                func.sum(Sale.quantity * Sale.price),
                0,
            )
        )
    )

    total_orders = db.scalar(
        select(
            func.count(
                func.distinct(Sale.invoice)
            )
        )
    )

    top_product = db.execute(
        select(
            Product.description,
            func.sum(Sale.quantity).label(
                "total_quantity"
            ),
        )
        .join(
            Sale,
            Sale.product_id == Product.id,
        )
        .group_by(
            Product.description
        )
        .order_by(
            func.sum(Sale.quantity).desc()
        )
        .limit(1)
    ).first()

    return {
        "status": "Access Granted",
        "total_revenue": round(
            float(total_revenue or 0),
            2,
        ),
        "total_orders": int(
            total_orders or 0
        ),
        "top_product": (
            top_product.description
            if top_product
            else "N/A"
        ),
    }