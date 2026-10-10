"""
SQLAlchemy Database ORM Models for Milestone 3 (MarketMind AI)
Includes foundational POS tables, segmentation, forecasting, recommendations, churn, and anomalies.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Customer(Base):
    __tablename__ = "customers"

    customer_id = Column(String(50), primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    orig_segment = Column(String(50), nullable=True)
    country = Column(String(50), nullable=True)
    city = Column(String(50), nullable=True)
    state = Column(String(50), nullable=True)
    postal_code = Column(String(20), nullable=True)
    region = Column(String(50), nullable=True)

class Product(Base):
    __tablename__ = "products"

    product_id = Column(String(50), primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    category = Column(String(100), nullable=True)
    sub_category = Column(String(100), nullable=True)
    unit_price = Column(Float, nullable=False)

class Sales(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(String(50), index=True, nullable=False)
    order_date = Column(DateTime, nullable=False)
    ship_date = Column(DateTime, nullable=True)
    ship_mode = Column(String(50), nullable=True)
    customer_id = Column(String(50), ForeignKey("customers.customer_id"), nullable=False)
    product_id = Column(String(50), ForeignKey("products.product_id"), nullable=False)
    sales_amount = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False)
    discount = Column(Float, default=0.0)
    profit = Column(Float, default=0.0)

class Inventory(Base):
    __tablename__ = "inventory"

    inventory_id = Column(Integer, primary_key=True, index=True)
    product_id = Column(String(50), ForeignKey("products.product_id"), nullable=False)
    stock_level = Column(Integer, nullable=False)
    reorder_point = Column(Integer, nullable=False)
    warehouse_region = Column(String(50), nullable=True)

class ClusterSummary(Base):
    __tablename__ = "cluster_summaries"

    cluster_id = Column(Integer, primary_key=True)
    segment_name = Column(String(100), nullable=False)
    customer_count = Column(Integer, nullable=False)
    pct_customers = Column(Float, nullable=True)
    total_sales = Column(Float, nullable=True)
    pct_sales = Column(Float, nullable=True)
    mean_recency_days = Column(Float, nullable=True)
    mean_frequency_orders = Column(Float, nullable=True)
    mean_monetary_sales = Column(Float, nullable=True)
    mean_order_value = Column(Float, nullable=True)
    mean_discount_rate = Column(Float, nullable=True)

class ModelMetric(Base):
    __tablename__ = "model_evaluation_metrics"

    id = Column(Integer, primary_key=True, index=True)
    model_name = Column(String(50), nullable=False)
    mae = Column(Float, nullable=False)
    rmse = Column(Float, nullable=False)
    r2_score = Column(Float, nullable=False)
    mape_pct = Column(Float, nullable=False)
    is_best_model = Column(Boolean, default=False)
    evaluated_at = Column(DateTime, default=datetime.utcnow)

# -------------------------------------------------------------
# MILESTONE 3 ORM MODELS
# -------------------------------------------------------------
class CustomerRecommendation(Base):
    __tablename__ = "customer_recommendations"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(String(50), ForeignKey("customers.customer_id"), index=True, nullable=False)
    rank = Column(Integer, nullable=False)
    recommended_product_id = Column(String(50), ForeignKey("products.product_id"), nullable=False)
    product_name = Column(String(255), nullable=False)
    category = Column(String(100), nullable=True)
    sub_category = Column(String(100), nullable=True)
    score = Column(Float, nullable=False)
    recommendation_type = Column(String(100), default="Collaborative Filtering")

class AssociationRule(Base):
    __tablename__ = "association_rules"

    id = Column(Integer, primary_key=True, index=True)
    antecedent_id = Column(String(50), nullable=False)
    antecedent_name = Column(String(255), nullable=False)
    consequent_id = Column(String(50), nullable=False)
    consequent_name = Column(String(255), nullable=False)
    support = Column(Float, nullable=False)
    confidence = Column(Float, nullable=False)
    lift = Column(Float, nullable=False)
    recommendation_type = Column(String(100), default="Cross-Sell / Frequently Bought Together")

class CustomerChurnPrediction(Base):
    __tablename__ = "customer_churn_predictions"

    customer_id = Column(String(50), primary_key=True, index=True)
    customer_name = Column(String(100), nullable=False)
    segment_name = Column(String(100), nullable=True)
    region = Column(String(50), nullable=True)
    recency_days = Column(Integer, nullable=False)
    frequency = Column(Integer, nullable=False)
    monetary = Column(Float, nullable=False)
    avg_order_value = Column(Float, nullable=False)
    churn_probability = Column(Float, nullable=False)
    risk_category = Column(String(50), nullable=False)

class TransactionAnomaly(Base):
    __tablename__ = "transaction_anomalies"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(String(50), nullable=False)
    order_date = Column(String(50), nullable=True)
    customer_name = Column(String(100), nullable=True)
    region = Column(String(50), nullable=True)
    product_name = Column(String(255), nullable=True)
    category = Column(String(100), nullable=True)
    sales_amount = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False)
    discount_pct = Column(Float, default=0.0)
    profit = Column(Float, default=0.0)
    anomaly_score = Column(Float, nullable=False)
    anomaly_reason = Column(Text, nullable=False)
