from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# --- Token Schemas ---
class Token(BaseModel):
    access_token: str
    token_type: str
    role: str
    username: str
    outlet_id: Optional[str] = None

class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None
    outlet_id: Optional[str] = None

# --- Staff Schemas ---
class StaffBase(BaseModel):
    username: str
    email: str
    full_name: Optional[str] = None
    role_id: int
    outlet_id: Optional[str] = None

class StaffCreate(StaffBase):
    password: str

class StaffOut(StaffBase):
    staff_id: int
    is_active: bool
    role_name: Optional[str] = None

    class Config:
        from_attributes = True

# --- Menu Schemas ---
class MenuItemOut(BaseModel):
    item_id: str
    item_name: str
    category: str
    unit_price: float
    stock_units: int
    reorder_level: int
    needs_restock: bool

    class Config:
        from_attributes = True

# --- Order Schemas ---
class OrderCreate(BaseModel):
    item_id: str
    quantity: int
    outlet_id: str
    patron_id: Optional[str] = "WALKIN"
    payment_mode: str

class OrderOut(BaseModel):
    order_id: str
    order_time: str
    item_id: str
    item_name: Optional[str] = None
    category: Optional[str] = None
    quantity: int
    unit_price: float
    total_amount: float
    outlet_id: str
    patron_id: Optional[str] = None
    payment_mode: str

    class Config:
        from_attributes = True

# --- Insights (Analytics) Schema ---
class CategoryRevenue(BaseModel):
    category: str
    total_revenue: float
    total_quantity: int

class InsightsSummary(BaseModel):
    total_revenue: float
    total_orders: int
    total_items_sold: int
    low_stock_count: int
    category_breakdown: List[CategoryRevenue]
    top_menu_items: List[dict]
    recent_orders: List[OrderOut]
