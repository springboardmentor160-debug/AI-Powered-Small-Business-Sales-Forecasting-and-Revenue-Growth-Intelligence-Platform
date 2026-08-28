from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, List
from datetime import datetime

from database import get_db
import models
import schemas

router = APIRouter(prefix="/api/v1/analytics", tags=["Analytics"])

@router.get("/summary", response_model=schemas.AnalyticsSummary)
def get_analytics_summary(
    store_id: Optional[str] = Query(None, description="Filter metrics by store_id"),
    db: Session = Depends(get_db)
):
    query = db.query(models.Transaction)
    if store_id:
        query = query.filter(models.Transaction.store_id == store_id)

    total_revenue = query.with_entities(func.sum(models.Transaction.total_amount)).scalar() or 0.0
    total_txns = query.count()
    total_items_sold = query.with_entities(func.sum(models.Transaction.quantity)).scalar() or 0

    # Low Stock Items count
    low_stock_count = db.query(models.Inventory).filter(
        models.Inventory.stock_level <= models.Inventory.reorder_threshold
    ).count()

    # Category Breakdown
    cat_query = db.query(
        models.Inventory.category,
        func.sum(models.Transaction.total_amount).label("rev"),
        func.sum(models.Transaction.quantity).label("qty")
    ).join(models.Transaction, models.Transaction.product_id == models.Inventory.product_id)

    if store_id:
        cat_query = cat_query.filter(models.Transaction.store_id == store_id)

    cat_results = cat_query.group_by(models.Inventory.category).all()
    category_breakdown = [
        schemas.CategorySales(
            category=cat,
            total_revenue=round(rev or 0.0, 2),
            total_quantity=qty or 0
        ) for cat, rev, qty in cat_results
    ]

    # Top Products
    top_prod_query = db.query(
        models.Inventory.product_name,
        models.Inventory.category,
        func.sum(models.Transaction.quantity).label("units_sold"),
        func.sum(models.Transaction.total_amount).label("revenue")
    ).join(models.Transaction, models.Transaction.product_id == models.Inventory.product_id)

    if store_id:
        top_prod_query = top_prod_query.filter(models.Transaction.store_id == store_id)

    top_prods = top_prod_query.group_by(
        models.Inventory.product_id, models.Inventory.product_name, models.Inventory.category
    ).order_by(func.sum(models.Transaction.total_amount).desc()).limit(5).all()

    top_products_list = [
        {
            "product_name": name,
            "category": cat,
            "units_sold": units or 0,
            "revenue": round(rev or 0.0, 2)
        } for name, cat, units, rev in top_prods
    ]

    # Recent Transactions
    recent_txs = query.order_by(models.Transaction.transaction_date.desc()).limit(10).all()
    recent_tx_list = []
    for tx in recent_txs:
        recent_tx_list.append(schemas.TransactionOut(
            transaction_id=tx.transaction_id,
            transaction_date=tx.transaction_date.strftime("%Y-%m-%d %H:%M:%S") if isinstance(tx.transaction_date, datetime) else str(tx.transaction_date),
            product_id=tx.product_id,
            product_name=tx.product.product_name if tx.product else "N/A",
            category=tx.product.category if tx.product else "N/A",
            quantity=tx.quantity,
            unit_price=tx.unit_price,
            total_amount=tx.total_amount,
            store_id=tx.store_id,
            customer_id=tx.customer_id,
            payment_method=tx.payment_method
        ))

    return schemas.AnalyticsSummary(
        total_revenue=round(total_revenue, 2),
        total_transactions=total_txns,
        total_items_sold=total_items_sold,
        low_stock_count=low_stock_count,
        category_breakdown=category_breakdown,
        top_products=top_products_list,
        recent_transactions=recent_tx_list
    )
