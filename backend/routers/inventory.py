from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from database import get_db
import models
import schemas

router = APIRouter(prefix="/api/v1/inventory", tags=["Inventory"])

@router.get("/", response_model=List[schemas.InventoryOut])
def get_inventory(
    low_stock_only: bool = Query(False, description="Filter items where stock_level <= reorder_threshold"),
    category: Optional[str] = Query(None, description="Filter by product category"),
    db: Session = Depends(get_db)
):
    query = db.query(models.Inventory)
    if category:
        query = query.filter(models.Inventory.category == category)
    
    items = query.all()
    
    result = []
    for item in items:
        needs_reorder = item.stock_level <= item.reorder_threshold
        if low_stock_only and not needs_reorder:
            continue
        
        result.append(schemas.InventoryOut(
            product_id=item.product_id,
            product_name=item.product_name,
            category=item.category,
            unit_price=item.unit_price,
            stock_level=item.stock_level,
            reorder_threshold=item.reorder_threshold,
            needs_reorder=needs_reorder
        ))
    return result

@router.put("/{product_id}/stock", response_model=schemas.InventoryOut)
def update_stock_level(
    product_id: str,
    new_stock: int = Query(..., ge=0),
    db: Session = Depends(get_db)
):
    item = db.query(models.Inventory).filter(models.Inventory.product_id == product_id).first()
    if not item:
        raise HTTPException(status_code=404, detail=f"Product with ID '{product_id}' not found")
    
    item.stock_level = new_stock
    db.commit()
    db.refresh(item)

    return schemas.InventoryOut(
        product_id=item.product_id,
        product_name=item.product_name,
        category=item.category,
        unit_price=item.unit_price,
        stock_level=item.stock_level,
        reorder_threshold=item.reorder_threshold,
        needs_reorder=item.stock_level <= item.reorder_threshold
    )
