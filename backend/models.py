from sqlalchemy import Column, Integer, String, Date, Float, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()


class Role(Base):
    __tablename__ = "roles"
    id = Column(String, primary_key=True)
    name = Column(String, unique=True, nullable=False)  
    users = relationship("User", back_populates="role")


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)  
    role_id = Column(String, ForeignKey("roles.id"))
    role = relationship("Role", back_populates="users")


class SalesTransaction(Base):
    __tablename__ = "sales_transactions"
    id = Column(Integer, primary_key=True)
    store_id = Column(String)
    product_id = Column(String, ForeignKey("products.product_id"))
    sales_rep_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    date = Column(Date)
    units_sold = Column(Integer)
    inventory_level = Column(Integer)
    demand = Column(Float)


class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True)
    customer_id = Column(String, ForeignKey("customers.customer_id"))
    date = Column(Date)
    product_category = Column(String)
    quantity = Column(Integer)
    price_per_unit = Column(Float)
    total_amount = Column(Float)

class Product(Base):
    __tablename__ = "products"
    product_id = Column(String,primary_key=True)
    category = Column(String)

class Customer(Base):
    __tablename__ = "customers"
    customer_id = Column(String, primary_key=True)
    gender = Column(String)
    age = Column(Integer)

    assigned_rep_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True
    )