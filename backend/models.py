from sqlalchemy import Column, Integer, Float, String, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from backend.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(120), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False)  # owner, manager, sales_executive, admin
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class Customer(Base):
    __tablename__ = "customers"

    id = Column(String(50), primary_key=True, index=True)  # e.g., C001, C002
    name = Column(String(120), nullable=False)
    contact_info = Column(String(200), nullable=True)

    sales = relationship("Sale", back_populates="customer")


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), unique=True, nullable=False)
    category = Column(String(80), nullable=False)
    unit_price = Column(Float, nullable=False)

    sales = relationship("Sale", back_populates="product")
    inventory = relationship("Inventory", back_populates="product", uselist=False)


class Sale(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, unique=True, index=True, nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    customer_id = Column(String(50), ForeignKey("customers.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    sale_date = Column(Date, nullable=False)

    product = relationship("Product", back_populates="sales")
    customer = relationship("Customer", back_populates="sales")
    invoice = relationship("Invoice", back_populates="sale", uselist=False)

    @property
    def total_amount(self) -> float:
        return round(self.quantity * self.unit_price, 2)


class Inventory(Base):
    __tablename__ = "inventory"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), unique=True, nullable=False)
    stock_level = Column(Integer, nullable=False)
    reorder_point = Column(Integer, nullable=False)

    product = relationship("Product", back_populates="inventory")

    @property
    def is_low_stock(self) -> bool:
        return self.stock_level < self.reorder_point


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    sale_id = Column(Integer, ForeignKey("sales.id"), unique=True, nullable=False)
    amount = Column(Float, nullable=False)
    payment_status = Column(String(50), nullable=False, default="PAID")  # PAID, PENDING

    sale = relationship("Sale", back_populates="invoice")