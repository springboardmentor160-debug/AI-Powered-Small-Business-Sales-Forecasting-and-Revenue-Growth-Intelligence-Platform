from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class Role(Base):
    __tablename__ = "roles"

    role_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    role_name = Column(String(50), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    users = relationship("User", back_populates="role")


class Store(Base):
    __tablename__ = "stores"

    store_id = Column(String(50), primary_key=True, index=True)
    store_name = Column(String(100), nullable=False)
    location = Column(String(150), nullable=True)
    contact_phone = Column(String(30), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    users = relationship("User", back_populates="store")
    transactions = relationship("Transaction", back_populates="store")


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=True)
    role_id = Column(Integer, ForeignKey("roles.role_id"), nullable=False)
    store_id = Column(String(50), ForeignKey("stores.store_id"), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    role = relationship("Role", back_populates="users")
    store = relationship("Store", back_populates="users")


class Customer(Base):
    __tablename__ = "customers"

    customer_id = Column(String(50), primary_key=True, index=True)
    customer_name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=True)
    phone = Column(String(30), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    transactions = relationship("Transaction", back_populates="customer")


class Inventory(Base):
    __tablename__ = "inventory"

    product_id = Column(String(50), primary_key=True, index=True)
    product_name = Column(String(150), nullable=False)
    category = Column(String(80), nullable=False, index=True)
    unit_price = Column(Float, nullable=False)
    stock_level = Column(Integer, nullable=False, default=0)
    reorder_threshold = Column(Integer, nullable=False, default=10)
    last_updated = Column(DateTime, default=datetime.utcnow)

    transactions = relationship("Transaction", back_populates="product")


class Transaction(Base):
    __tablename__ = "transactions"

    transaction_id = Column(String(50), primary_key=True, index=True)
    transaction_date = Column(DateTime, nullable=False, index=True)
    product_id = Column(String(50), ForeignKey("inventory.product_id"), nullable=False, index=True)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    total_amount = Column(Float, nullable=False)
    store_id = Column(String(50), ForeignKey("stores.store_id"), nullable=False, index=True)
    customer_id = Column(String(50), ForeignKey("customers.customer_id"), nullable=True)
    payment_method = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    product = relationship("Inventory", back_populates="transactions")
    store = relationship("Store", back_populates="transactions")
    customer = relationship("Customer", back_populates="transactions")
