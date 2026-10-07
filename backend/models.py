from sqlalchemy import Column, Integer, String, Date, DateTime, Float, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

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


class Product(Base):
    __tablename__ = "products"
    product_id = Column(String, primary_key=True)
    category = Column(String)


class Customer(Base):
    __tablename__ = "customers"
    # CustomerID from the Online Retail dataset (M2 segmentation source).
    # Gender/Age dropped here: the new dataset doesn't provide them, and
    # the old retail_sales_dataset_final.csv (M1) they came from is no
    # longer the active source for customer-level data.
    customer_id = Column(String, primary_key=True)
    country = Column(String)
    assigned_rep_id = Column(Integer, ForeignKey("users.id"), nullable=True)


class SalesTransaction(Base):
    __tablename__ = "sales_transactions"
    # Unchanged -- still backed by sales_data_prepped.csv (M1 inventory/
    # forecasting dataset). No customer_id here by design: this table is
    # a daily store/product aggregate, not a per-customer purchase record.
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
    # Rebuilt for the Online Retail dataset (online_retail_prepped.csv).
    # Replaces the old product_category/quantity/price_per_unit shape,
    # which matched retail_sales_dataset_final.csv and is no longer the
    # active source.
    id = Column(Integer, primary_key=True)
    invoice_no = Column(String)
    stock_code = Column(String)
    description = Column(String)
    customer_id = Column(String, ForeignKey("customers.customer_id"))
    date = Column(DateTime)
    quantity = Column(Integer)
    unit_price = Column(Float)
    total_amount = Column(Float)