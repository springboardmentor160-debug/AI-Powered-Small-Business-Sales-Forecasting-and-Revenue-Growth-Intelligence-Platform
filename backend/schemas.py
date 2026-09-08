from typing import Optional, List
from datetime import date, datetime
from pydantic import BaseModel, ConfigDict, EmailStr


# ==================== AUTH & USER SCHEMAS ====================

class UserLogin(BaseModel):
    username: str  # Can be username alias (owner, manager, exec, admin) or full email
    password: str


class UserRegister(BaseModel):
    name: str
    email: str
    password: str
    role: str = "sales_executive"  # Default role


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# ==================== SALES SCHEMAS ====================

class SaleItemResponse(BaseModel):
    id: int
    order_id: int
    product_id: int
    product_name: str
    category: str
    customer_id: str
    customer_name: str
    quantity: int
    unit_price: float
    total_amount: float
    sale_date: date
    payment_status: Optional[str] = "PAID"

    model_config = ConfigDict(from_attributes=True)


class SalesSummaryResponse(BaseModel):
    total_revenue: float
    total_orders: int
    total_units: int
    average_order_value: float
    top_product: str


# ==================== INVENTORY SCHEMAS ====================

class InventoryItemResponse(BaseModel):
    id: int
    product_id: int
    product_name: str
    category: str
    unit_price: float
    stock_level: int
    reorder_point: int
    is_low_stock: bool

    model_config = ConfigDict(from_attributes=True)


# ==================== ANALYTICS SCHEMAS ====================

class TopProductItem(BaseModel):
    product_name: str
    units_sold: int
    total_revenue: float


class SalesTrendItem(BaseModel):
    date: str
    revenue: float
    orders_count: int


class AnalyticsSummaryResponse(BaseModel):
    total_revenue: float
    total_orders: int
    total_units: int
    average_order_value: float
    top_product: str
    inventory_alerts_count: int
    top_products: List[TopProductItem]
    sales_trend: List[SalesTrendItem]
    planned_features_note: str
