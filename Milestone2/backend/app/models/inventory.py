from sqlalchemy import Column, Integer, String, Float, ForeignKey

from app.database.database import Base


class Inventory(Base):
    __tablename__ = "inventory"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(String(50), ForeignKey("products.product_id"), nullable=False)
    product_name = Column(String(150), nullable=False)
    category = Column(String(100))
    stock_level = Column(Integer, nullable=False)
    reorder_point = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    warehouse = Column(String(150))
