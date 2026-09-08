from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.database import get_db
from backend.models import Sale, Product, Customer, Invoice, User
from backend.schemas import SaleItemResponse, SalesSummaryResponse
from backend.dependencies import require_roles

router = APIRouter(prefix="/api/v1/sales", tags=["Sales"])


@router.get("", response_model=List[SaleItemResponse])
def get_sales(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["owner", "manager", "sales_executive", "admin"])),
):
    """Retrieve all sales transactions with linked product and customer details."""
    sales = (
        db.query(Sale)
        .join(Product, Sale.product_id == Product.id)
        .join(Customer, Sale.customer_id == Customer.id)
        .outerjoin(Invoice, Invoice.sale_id == Sale.id)
        .order_by(Sale.sale_date.asc(), Sale.order_id.asc())
        .all()
    )

    results = []
    for s in sales:
        results.append(
            SaleItemResponse(
                id=s.id,
                order_id=s.order_id,
                product_id=s.product_id,
                product_name=s.product.name,
                category=s.product.category,
                customer_id=s.customer_id,
                customer_name=s.customer.name,
                quantity=s.quantity,
                unit_price=s.unit_price,
                total_amount=s.total_amount,
                sale_date=s.sale_date,
                payment_status=s.invoice.payment_status if s.invoice else "PAID",
            )
        )
    return results


@router.get("/summary", response_model=SalesSummaryResponse)
def get_sales_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["owner", "manager", "sales_executive", "admin"])),
):
    """Compute aggregate sales metrics across all orders."""
    sales = db.query(Sale).all()

    if not sales:
        return SalesSummaryResponse(
            total_revenue=0.0,
            total_orders=0,
            total_units=0,
            average_order_value=0.0,
            top_product="N/A",
        )

    total_orders = len(sales)
    total_units = sum(s.quantity for s in sales)
    total_revenue = round(sum(s.quantity * s.unit_price for s in sales), 2)
    average_order_value = round(total_revenue / total_orders, 2) if total_orders > 0 else 0.0

    # Determine top product by units sold / revenue
    product_revenue_map = {}
    for s in sales:
        name = s.product.name if s.product else f"Product {s.product_id}"
        product_revenue_map[name] = product_revenue_map.get(name, 0.0) + (s.quantity * s.unit_price)

    top_product = max(product_revenue_map, key=product_revenue_map.get) if product_revenue_map else "N/A"

    return SalesSummaryResponse(
        total_revenue=total_revenue,
        total_orders=total_orders,
        total_units=total_units,
        average_order_value=average_order_value,
        top_product=top_product,
    )
