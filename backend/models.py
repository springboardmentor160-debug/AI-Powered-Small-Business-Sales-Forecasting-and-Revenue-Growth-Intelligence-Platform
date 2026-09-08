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

    staff = relationship("Staff", back_populates="role")


class Outlet(Base):
    __tablename__ = "outlets"

    outlet_id = Column(String(50), primary_key=True, index=True)
    outlet_name = Column(String(100), nullable=False)
    city = Column(String(100), nullable=True)
    contact_phone = Column(String(30), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    staff = relationship("Staff", back_populates="outlet")
    orders = relationship("Order", back_populates="outlet")


class Staff(Base):
    __tablename__ = "staff"

    staff_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=True)
    role_id = Column(Integer, ForeignKey("roles.role_id"), nullable=False)
    outlet_id = Column(String(50), ForeignKey("outlets.outlet_id"), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    role = relationship("Role", back_populates="staff")
    outlet = relationship("Outlet", back_populates="staff")


class Patron(Base):
    __tablename__ = "patrons"

    patron_id = Column(String(50), primary_key=True, index=True)
    patron_name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=True)
    phone = Column(String(30), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    orders = relationship("Order", back_populates="patron")


class MenuItem(Base):
    __tablename__ = "menu_items"

    item_id = Column(String(50), primary_key=True, index=True)
    item_name = Column(String(150), nullable=False)
    category = Column(String(80), nullable=False, index=True)
    unit_price = Column(Float, nullable=False)
    stock_units = Column(Integer, nullable=False, default=0)
    reorder_level = Column(Integer, nullable=False, default=10)
    last_updated = Column(DateTime, default=datetime.utcnow)

    orders = relationship("Order", back_populates="item")


class Order(Base):
    __tablename__ = "orders"

    order_id = Column(String(50), primary_key=True, index=True)
    order_time = Column(DateTime, nullable=False, index=True)
    item_id = Column(String(50), ForeignKey("menu_items.item_id"), nullable=False, index=True)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    total_amount = Column(Float, nullable=False)
    outlet_id = Column(String(50), ForeignKey("outlets.outlet_id"), nullable=False, index=True)
    patron_id = Column(String(50), ForeignKey("patrons.patron_id"), nullable=True)
    payment_mode = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    item = relationship("MenuItem", back_populates="orders")
    outlet = relationship("Outlet", back_populates="orders")
    patron = relationship("Patron", back_populates="orders")
