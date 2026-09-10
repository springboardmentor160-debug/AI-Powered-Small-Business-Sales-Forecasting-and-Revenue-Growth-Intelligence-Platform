from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey

from app.database.database import Base


class Sale(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(String(50), unique=True, index=True, nullable=False)
    order_date = Column(Date, nullable=False)
    product_id = Column(String(50), ForeignKey("products.product_id"), nullable=False)
    product_name = Column(String(150), nullable=False)
    customer_id = Column(String(50), ForeignKey("customers.customer_id"), nullable=False)
    quantity = Column(Float, nullable=False)
    unit_price = Column(Float, nullable=False)
    revenue = Column(Float, nullable=False)
