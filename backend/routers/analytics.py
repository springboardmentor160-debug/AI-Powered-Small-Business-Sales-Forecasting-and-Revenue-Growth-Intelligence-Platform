from collections import defaultdict
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import Sale, Product, Inventory, User
from backend.schemas import AnalyticsSummaryResponse, TopProductItem, SalesTrendItem
from backend.dependencies import require_roles

router = APIRouter(prefix="/api/v1/analytics", tags=["Analytics"])


@router.get("/summary", response_model=AnalyticsSummaryResponse)
def get_analytics_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["owner", "manager", "admin", "sales_executive"])),
):
    """Aggregate dashboard metrics including KPIs, product breakdown, and daily sales trend."""
    sales = db.query(Sale).join(Product, Sale.product_id == Product.id).all()
    inventory_items = db.query(Inventory).all()

    total_orders = len(sales)
    total_units = sum(s.quantity for s in sales)
    total_revenue = round(sum(s.quantity * s.unit_price for s in sales), 2)
    average_order_value = round(total_revenue / total_orders, 2) if total_orders > 0 else 0.0

    # Count inventory alerts
    inventory_alerts_count = sum(1 for item in inventory_items if item.is_low_stock)

    # Aggregate by product
    product_stats = defaultdict(lambda: {"units": 0, "revenue": 0.0})
    for s in sales:
        p_name = s.product.name
        product_stats[p_name]["units"] += s.quantity
        product_stats[p_name]["revenue"] += round(s.quantity * s.unit_price, 2)

    top_products = [
        TopProductItem(
            product_name=name,
            units_sold=data["units"],
            total_revenue=round(data["revenue"], 2),
        )
        for name, data in sorted(product_stats.items(), key=lambda item: item[1]["revenue"], reverse=True)
    ]

    top_product_name = top_products[0].product_name if top_products else "N/A"

    # Aggregate sales trend by date
    daily_stats = defaultdict(lambda: {"revenue": 0.0, "orders": 0})
    for s in sales:
        date_str = s.sale_date.strftime("%Y-%m-%d")
        daily_stats[date_str]["revenue"] += round(s.quantity * s.unit_price, 2)
        daily_stats[date_str]["orders"] += 1

    sales_trend = [
        SalesTrendItem(
            date=d,
            revenue=round(val["revenue"], 2),
            orders_count=val["orders"],
        )
        for d, val in sorted(daily_stats.items())
    ]

    return AnalyticsSummaryResponse(
        total_revenue=total_revenue,
        total_orders=total_orders,
        total_units=total_units,
        average_order_value=average_order_value,
        top_product=top_product_name,
        inventory_alerts_count=inventory_alerts_count,
        top_products=top_products,
        sales_trend=sales_trend,
        planned_features_note="Milestone 1 Foundation Active. AI Forecasting, Churn Prediction, and Customer Segmentation are scheduled for Milestone 2.",
    )
