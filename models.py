from sqlalchemy import Column, Integer, String, Numeric, DateTime
from database import Base


class Customer(Base):
    __tablename__ = "customers"

    customer_id = Column(Integer, primary_key=True)
    country = Column(String)


class Product(Base):
    __tablename__ = "products"

    product_id = Column(String, primary_key=True)
    product_name = Column(String)


class Inventory(Base):
    __tablename__ = "inventory"

    product_id = Column(String, primary_key=True)
    current_stock = Column(Integer)
    reorder_threshold = Column(Integer)


class SalesTransaction(Base):
    __tablename__ = "sales_transactions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    invoice_id = Column(Integer)
    product_id = Column(String)
    customer_id = Column(Integer)
    quantity = Column(Integer)
    unit_price = Column(Numeric)
    invoice_date = Column(DateTime)
    sales_amount = Column(Numeric)
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False, default="user")