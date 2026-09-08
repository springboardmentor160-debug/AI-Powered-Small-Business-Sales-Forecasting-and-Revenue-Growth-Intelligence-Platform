from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from database import get_db
import models
import schemas

router = APIRouter(prefix="/api/v1/menu", tags=["Menu & Stock"])


@router.get("/", response_model=List[schemas.MenuItemOut])
def get_menu(
    low_stock_only: bool = Query(False, description="Only items at or below reorder_level"),
    category: Optional[str] = Query(None, description="Filter by category"),
    db: Session = Depends(get_db)
):
    query = db.query(models.MenuItem)
    if category:
        query = query.filter(models.MenuItem.category == category)

    result = []
    for item in query.all():
        needs_restock = item.stock_units <= item.reorder_level
        if low_stock_only and not needs_restock:
            continue
        result.append(schemas.MenuItemOut(
            item_id=item.item_id,
            item_name=item.item_name,
            category=item.category,
            unit_price=item.unit_price,
            stock_units=item.stock_units,
            reorder_level=item.reorder_level,
            needs_restock=needs_restock
        ))
    return result


@router.put("/{item_id}/stock", response_model=schemas.MenuItemOut)
def update_stock(
    item_id: str,
    new_stock: int = Query(..., ge=0),
    db: Session = Depends(get_db)
):
    item = db.query(models.MenuItem).filter(models.MenuItem.item_id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail=f"Menu item '{item_id}' not found")

    item.stock_units = new_stock
    db.commit()
    db.refresh(item)

    return schemas.MenuItemOut(
        item_id=item.item_id,
        item_name=item.item_name,
        category=item.category,
        unit_price=item.unit_price,
        stock_units=item.stock_units,
        reorder_level=item.reorder_level,
        needs_restock=item.stock_units <= item.reorder_level
    )
