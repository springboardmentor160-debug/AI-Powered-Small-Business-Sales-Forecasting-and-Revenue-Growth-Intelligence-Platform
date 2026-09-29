"""
Pydantic Data Models for Milestone 2 API (MarketMind AI)
"""

from pydantic import BaseModel, EmailStr
from typing import List, Dict, Any, Optional

class LoginRequest(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: Dict[str, Any]

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str

class UserCreateRequest(BaseModel):
    name: str
    email: str
    role: str
    password: str

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

class ClusterSummaryItem(BaseModel):
    cluster_id: int
    segment_name: str
    customer_count: int
    pct_customers: float
    total_sales: float
    pct_sales: float
    mean_recency_days: float
    mean_frequency_orders: float
    mean_monetary_sales: float
    mean_order_value: float
    mean_discount_rate: float

class CustomerItem(BaseModel):
    customer_id: str
    customer_name: str
    orig_segment: str
    region: str
    recency_days: float
    frequency_orders: int
    monetary_sales: float
    avg_order_value: float
    total_profit: float
    avg_discount: float
    kmeans_cluster: int
    hierarchical_cluster: int
    segment_name: str

class BusinessOwnerDashboardResponse(BaseModel):
    role: str = "Business Owner"
    kpis: OverviewKPI
    insights: List[NaturalInsight]
    top_segments: List[ClusterSummaryItem]

class StoreManagerDashboardResponse(BaseModel):
    role: str = "Store Manager"
    total_sales: float
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
    top_customers: List[CustomerItem]

class AdminDashboardResponse(BaseModel):
    role: str = "Administrator"
    total_users: int
    total_transactions: int
    total_customers: int
    best_model: str
    insights: List[NaturalInsight]
