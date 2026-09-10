from sqlalchemy import Column, Integer, String, Float

from app.database.database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(String(50), unique=True, index=True, nullable=False)
    product_name = Column(String(150), nullable=False)
    category = Column(String(100))
    unit_price = Column(Float, nullable=False)
