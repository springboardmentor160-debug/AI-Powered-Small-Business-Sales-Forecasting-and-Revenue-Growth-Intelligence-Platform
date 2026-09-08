from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from datetime import datetime

from database import get_db
import models
import schemas
from auth import get_current_user
from routers.orders import _to_order_out

router = APIRouter(prefix="/api/v1/insights", tags=["Insights"])


@router.get("/summary", response_model=schemas.InsightsSummary)
def get_summary(
    outlet_id: Optional[str] = Query(None, description="Filter metrics by outlet_id"),
    current_user: Optional[models.Staff] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    role_name = current_user.role.role_name if (current_user and current_user.role) else "franchise_owner"
    user_outlet = current_user.outlet_id if current_user else None

    # Outlet Manager & Waiter are locked to their own outlet
    effective_outlet_id = outlet_id
    if role_name in ["outlet_manager", "waiter"] and user_outlet:
        effective_outlet_id = user_outlet

    query = db.query(models.Order)
    if effective_outlet_id:
        query = query.filter(models.Order.outlet_id == effective_outlet_id)

    total_revenue = query.with_entities(func.sum(models.Order.total_amount)).scalar() or 0.0
    total_orders = query.count()
    total_items_sold = query.with_entities(func.sum(models.Order.quantity)).scalar() or 0

    low_stock_count = db.query(models.MenuItem).filter(
        models.MenuItem.stock_units <= models.MenuItem.reorder_level
    ).count()

    cat_query = db.query(
        models.MenuItem.category,
        func.sum(models.Order.total_amount).label("rev"),
        func.sum(models.Order.quantity).label("qty")
    ).join(models.Order, models.Order.item_id == models.MenuItem.item_id)
    if effective_outlet_id:
        cat_query = cat_query.filter(models.Order.outlet_id == effective_outlet_id)
    cat_results = cat_query.group_by(models.MenuItem.category).all()
    category_breakdown = [
        schemas.CategoryRevenue(category=cat, total_revenue=round(rev or 0.0, 2), total_quantity=qty or 0)
        for cat, rev, qty in cat_results
    ]

    top_query = db.query(
        models.MenuItem.item_name,
        models.MenuItem.category,
        func.sum(models.Order.quantity).label("units_sold"),
        func.sum(models.Order.total_amount).label("revenue")
    ).join(models.Order, models.Order.item_id == models.MenuItem.item_id)
    if effective_outlet_id:
        top_query = top_query.filter(models.Order.outlet_id == effective_outlet_id)
    top_items = top_query.group_by(
        models.MenuItem.item_id, models.MenuItem.item_name, models.MenuItem.category
    ).order_by(func.sum(models.Order.total_amount).desc()).limit(5).all()

    top_menu_items = [
        {"item_name": name, "category": cat, "units_sold": units or 0, "revenue": round(rev or 0.0, 2)}
        for name, cat, units, rev in top_items
    ]

    recent = query.order_by(models.Order.order_time.desc()).limit(10).all()
    recent_orders = [_to_order_out(o) for o in recent]

    return schemas.InsightsSummary(
        total_revenue=round(total_revenue, 2),
        total_orders=total_orders,
        total_items_sold=total_items_sold,
        low_stock_count=low_stock_count,
        category_breakdown=category_breakdown,
        top_menu_items=top_menu_items,
        recent_orders=recent_orders
    )
