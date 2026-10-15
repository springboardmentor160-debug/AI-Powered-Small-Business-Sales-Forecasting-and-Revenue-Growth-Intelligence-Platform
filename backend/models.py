from datetime import datetime, timezone
from sqlalchemy import Column, Date, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from database import Base


def utcnow():
    """Naive UTC timestamp (SQLite has no timezone type)."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


class Role(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True)
    name = Column(String(30), unique=True, nullable=False)   # business_owner | store_manager | sales_executive | admin


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    created_at = Column(DateTime, default=utcnow)
    role = relationship("Role")


class Product(Base):
    """Store catalogue (from datasets/processed/product_lookup.csv)."""
    __tablename__ = "products"
    id = Column(Integer, primary_key=True)
    product_id = Column(String(20), unique=True, index=True, nullable=False)
    category = Column(String(50))
    avg_price = Column(Float)


class Customer(Base):
    """Online-retail customers (from online_retail_prepped.csv)."""
    __tablename__ = "customers"
    id = Column(Integer, primary_key=True)
    customer_id = Column(String(20), unique=True, index=True, nullable=False)
    country = Column(String(60))


class SalesTransaction(Base):
    """Daily store/product sales + inventory rows (sales_data_prepped.csv). Column names match the CSV."""
    __tablename__ = "sales_transactions"
    id = Column(Integer, primary_key=True)
    date = Column(Date, index=True, nullable=False)
    store_id = Column(String(10), index=True)
    product_id = Column(String(20), index=True)
    category = Column(String(50), index=True)
    region = Column(String(30))
    inventory_level = Column(Integer)
    units_sold = Column(Integer)
    units_ordered = Column(Integer)
    demand_forecast = Column(Float)
    price = Column(Float)
    discount = Column(Integer)
    weather_condition = Column(String(30))
    holiday_promotion = Column(Integer)
    competitor_pricing = Column(Float)
    seasonality = Column(String(20))
    net_price = Column(Float)
    revenue = Column(Float)
    reorder_point = Column(Integer)


class Transaction(Base):
    """Online-retail invoice lines (online_retail_prepped.csv)."""
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True)
    invoice_no = Column(String(20), index=True)
    stock_code = Column(String(30), index=True)
    description = Column(String(255))
    quantity = Column(Integer)
    invoice_date = Column(DateTime, index=True)
    unit_price = Column(Float)
    customer_id = Column(String(20), index=True)
    country = Column(String(60))
    total_amount = Column(Float)


class Invoice(Base):
    __tablename__ = "invoices"
    id = Column(Integer, primary_key=True)
    customer_id = Column(String(20), index=True)
    description = Column(String(255))
    amount = Column(Float, nullable=False)
    payment_status = Column(String(15), default="pending")      # pending | paid | overdue
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    created_at = Column(DateTime, default=utcnow)


class PasswordResetToken(Base):
    """One-time password-reset link. Only a SHA-256 hash of the token is stored."""
    __tablename__ = "password_reset_tokens"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    token_hash = Column(String(64), unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=utcnow)
    expires_at = Column(DateTime, nullable=False)
    used_at = Column(DateTime, nullable=True)
