from collections import defaultdict

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database.database import get_db
from app.models.inventory import Inventory
from app.models.sale import Sale
from app.models.user import User

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/summary")
def dashboard_summary(
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    total_revenue = db.query(func.coalesce(func.sum(Sale.revenue), 0)).scalar()
    total_orders = db.query(func.count(Sale.id)).scalar()
    total_customers = db.query(func.count(func.distinct(Sale.customer_id))).scalar()
    total_products = db.query(func.count(func.distinct(Sale.product_id))).scalar()

    top = (
        db.query(
            Sale.product_name,
            func.sum(Sale.revenue).label("revenue")
        )
        .group_by(Sale.product_name)
        .order_by(func.sum(Sale.revenue).desc())
        .first()
    )

    low_stock = (
        db.query(func.count(Inventory.id))
        .filter(Inventory.stock_level < Inventory.reorder_point)
        .scalar()
    )

    return {
        "total_revenue": round(float(total_revenue or 0), 2),
        "total_orders": int(total_orders or 0),
        "total_customers": int(total_customers or 0),
        "total_products": int(total_products or 0),
        "top_product": top.product_name if top else "N/A",
        "low_stock_items": int(low_stock or 0),
    }


@router.get("/sales-trend")
def sales_trend(
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    rows = (
        db.query(
            Sale.order_date,
            func.sum(Sale.revenue).label("revenue")
        )
        .group_by(Sale.order_date)
        .order_by(Sale.order_date)
        .all()
    )

    return [
        {
            "date": row.order_date.isoformat(),
            "revenue": round(float(row.revenue or 0), 2),
        }
        for row in rows
    ]


@router.get("/top-products")
def top_products(
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    rows = (
        db.query(
            Sale.product_name,
            func.sum(Sale.quantity).label("quantity"),
            func.sum(Sale.revenue).label("revenue"),
        )
        .group_by(Sale.product_name)
        .order_by(func.sum(Sale.revenue).desc())
        .limit(5)
        .all()
    )

    return [
        {
            "product_name": row.product_name,
            "quantity": float(row.quantity or 0),
            "revenue": round(float(row.revenue or 0), 2),
        }
        for row in rows
    ]
