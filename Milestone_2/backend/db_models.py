"""
SQLAlchemy Database Models for Milestone 2 (MarketMind AI)
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Date, Boolean, ForeignKey, Numeric, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False) # 'Business Owner', 'Store Manager', 'Sales Executive', 'Administrator'
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Customer(Base):
    __tablename__ = "customers"

    customer_id = Column(String(50), primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    orig_segment = Column(String(50))
    country = Column(String(100))
    city = Column(String(100))
    state = Column(String(100))
    postal_code = Column(String(20))
    region = Column(String(50))

    sales_records = relationship("Sales", back_populates="customer")
    segmentation = relationship("SegmentationResult", back_populates="customer", uselist=False)


class Product(Base):
    __tablename__ = "products"

    product_id = Column(String(50), primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    category = Column(String(100), nullable=False)
    sub_category = Column(String(100), nullable=False)
    unit_price = Column(Float, default=0.0)

    sales_records = relationship("Sales", back_populates="product")
    inventory_items = relationship("Inventory", back_populates="product")

class Geography(Base):
    __tablename__ = "geography"

    id = Column(Integer, primary_key=True, index=True)
    country = Column(String(100))
    city = Column(String(100))
    state = Column(String(100))
    postal_code = Column(String(20))
    region = Column(String(50))

class Sales(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(String(50), nullable=False, index=True)
    order_date = Column(Date, nullable=False, index=True)
    ship_date = Column(Date)
    ship_mode = Column(String(50))
    customer_id = Column(String(50), ForeignKey("customers.customer_id"), index=True)
    product_id = Column(String(50), ForeignKey("products.product_id"), index=True)
    sales_amount = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False)
    discount = Column(Float, default=0.0)
    profit = Column(Float, default=0.0)

    customer = relationship("Customer", back_populates="sales_records")
    product = relationship("Product", back_populates="sales_records")

class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    sale_id = Column(Integer, nullable=False)
    amount = Column(Float, nullable=False)
    payment_status = Column(String(50), default="Paid")


class Inventory(Base):
    __tablename__ = "inventory"

    inventory_id = Column(Integer, primary_key=True, index=True)
    product_id = Column(String(50), ForeignKey("products.product_id"), index=True)
    stock_level = Column(Integer, nullable=False)
    reorder_point = Column(Integer, default=10)
    warehouse_region = Column(String(50))

    product = relationship("Product", back_populates="inventory_items")

class SegmentationResult(Base):
    __tablename__ = "segmentation_results"

    customer_id = Column(String(50), ForeignKey("customers.customer_id"), primary_key=True, index=True)
    recency_days = Column(Float)
    frequency_orders = Column(Integer)
    monetary_sales = Column(Float)
    avg_order_value = Column(Float)
    total_profit = Column(Float)
    avg_discount = Column(Float)
    kmeans_cluster = Column(Integer)
    hierarchical_cluster = Column(Integer)
    segment_name = Column(String(100), index=True)

    customer = relationship("Customer", back_populates="segmentation")

class ClusterSummary(Base):
    __tablename__ = "cluster_summaries"

    cluster_id = Column(Integer, primary_key=True, index=True)
    segment_name = Column(String(100), nullable=False)
    customer_count = Column(Integer, nullable=False)
    pct_customers = Column(Float)
    total_sales = Column(Float)
    pct_sales = Column(Float)
    mean_recency_days = Column(Float)
    mean_frequency_orders = Column(Float)
    mean_monetary_sales = Column(Float)
    mean_order_value = Column(Float)
    mean_discount_rate = Column(Float)

class ForecastResult(Base):
    __tablename__ = "forecast_results"

    id = Column(Integer, primary_key=True, index=True)
    ds = Column(Date, nullable=False, index=True)
    actual_sales = Column(Float, nullable=True)
    profit = Column(Float, nullable=True)
    prophet_yhat = Column(Float, nullable=True)
    prophet_lower = Column(Float, nullable=True)
    prophet_upper = Column(Float, nullable=True)
    xgboost_yhat = Column(Float, nullable=True)
    xgboost_lower = Column(Float, nullable=True)
    xgboost_upper = Column(Float, nullable=True)
    rf_yhat = Column(Float, nullable=True)
    rf_lower = Column(Float, nullable=True)
    rf_upper = Column(Float, nullable=True)

class ModelMetric(Base):
    __tablename__ = "model_evaluation_metrics"

    id = Column(Integer, primary_key=True, index=True)
    model_name = Column(String(50), unique=True, nullable=False) # 'Prophet', 'XGBoost', 'Random Forest'
    mae = Column(Float, nullable=False)
    rmse = Column(Float, nullable=False)
    r2_score = Column(Float, nullable=False)
    mape_pct = Column(Float, nullable=False)
    is_best_model = Column(Boolean, default=False)
    evaluated_at = Column(DateTime(timezone=True), server_default=func.now())
