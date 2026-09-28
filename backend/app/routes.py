"""Initial MarketMind summary routes."""

from fastapi import APIRouter

from .services import get_customer_summary, get_inventory_summary, get_sales_summary


router = APIRouter(prefix="/api")


@router.get("/sales/summary")
def sales_summary() -> dict:
    """Return aggregate sales metrics from processed data."""
    return get_sales_summary()


@router.get("/inventory/summary")
def inventory_summary() -> dict:
    """Return aggregate inventory metrics from processed data."""
    return get_inventory_summary()


@router.get("/customers/summary")
def customer_summary() -> dict:
    """Return aggregate customer metrics from processed data."""
    return get_customer_summary()
