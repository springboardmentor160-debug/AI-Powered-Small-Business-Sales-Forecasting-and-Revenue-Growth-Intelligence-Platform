"""
Pydantic Data Schemas for API Requests & Responses (Milestone 3)
"""

from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    user_name: str
    email: str
    user: Optional[Dict[str, Any]] = None


class LoginRequest(BaseModel):
    email: str
    password: str

class UserCreateRequest(BaseModel):
    name: str
    email: str
    password: str
    role: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str

class NaturalInsight(BaseModel):
    type: str
    title: str
    message: str

class OverviewKPI(BaseModel):
    total_sales: float
    total_customers: int
    total_orders: int
    best_forecasting_model: str
    best_model_rmse: float
    top_customer_segment: str

class RecommendationItem(BaseModel):
    customer_id: str
    rank: int
    recommended_product_id: str
    product_name: str
    category: Optional[str] = None
    sub_category: Optional[str] = None
    score: float
    recommendation_type: str = "Collaborative Filtering"

class AssociationRuleItem(BaseModel):
    antecedent_id: str
    antecedent_name: str
    consequent_id: str
    consequent_name: str
    support: float
    confidence: float
    lift: float
    recommendation_type: str = "Cross-Sell / Frequently Bought Together"

class ChurnCustomerItem(BaseModel):
    customer_id: str
    customer_name: str
    segment_name: Optional[str] = None
    region: Optional[str] = None
    recency_days: int
    frequency: int
    monetary: float
    avg_order_value: float
    churn_probability: float
    risk_category: str

class TransactionAnomalyItem(BaseModel):
    id: int
    order_id: str
    order_date: Optional[str] = None
    customer_name: Optional[str] = None
    region: Optional[str] = None
    product_name: Optional[str] = None
    category: Optional[str] = None
    sales_amount: float
    quantity: int
    discount_pct: float
    profit: float
    anomaly_score: float
    anomaly_reason: str

class BusinessOwnerDashboardResponse(BaseModel):
    role: str = "Business Owner"
    kpis: OverviewKPI
    insights: List[NaturalInsight]
    top_segments: List[Any]

class StoreManagerDashboardResponse(BaseModel):
    role: str = "Store Manager"
    total_sales: float
    total_orders: int = 0
    top_region: str
    top_category: str
    total_inventory_items: int
    insights: List[NaturalInsight]

class SalesExecutiveDashboardResponse(BaseModel):
    role: str = "Sales Executive"
    total_customers: int
    avg_order_value: float
    at_risk_count: int
    champions_count: int
    insights: List[NaturalInsight]

class AdminDashboardResponse(BaseModel):
    role: str = "Administrator"
    total_users: int
    total_transactions: int
    total_customers: int
    best_model: str
    insights: List[NaturalInsight]
