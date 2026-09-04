from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# --- Token Schemas ---
class Token(BaseModel):
    access_token: str
    token_type: str
    role: str
    username: str
    store_id: Optional[str] = None

class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None
    store_id: Optional[str] = None

# --- User Schemas ---
class UserBase(BaseModel):
    username: str
    email: str
    full_name: Optional[str] = None
    role_id: int
    store_id: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserOut(UserBase):
    user_id: int
    is_active: bool
    role_name: Optional[str] = None

    class Config:
        from_attributes = True

# --- Inventory Schemas ---
class InventoryOut(BaseModel):
    product_id: str
    product_name: str
    category: str
    unit_price: float
    stock_level: int
    reorder_threshold: int
    needs_reorder: bool

    class Config:
        from_attributes = True

# --- Transaction Schemas ---
class TransactionCreate(BaseModel):
    product_id: str
    quantity: int
    store_id: str
    customer_id: Optional[str] = "GUEST"
    payment_method: str

class TransactionOut(BaseModel):
    transaction_id: str
    transaction_date: str
    product_id: str
    product_name: Optional[str] = None
    category: Optional[str] = None
    quantity: int
    unit_price: float
    total_amount: float
    store_id: str
    customer_id: Optional[str] = None
    payment_method: str

    class Config:
        from_attributes = True

# --- Analytics Summary Schema ---
class CategorySales(BaseModel):
    category: str
    total_revenue: float
    total_quantity: int

class AnalyticsSummary(BaseModel):
    total_revenue: float
    total_transactions: int
    total_items_sold: int
    low_stock_count: int
    category_breakdown: List[CategorySales]
    top_products: List[dict]
    recent_transactions: List[TransactionOut]
