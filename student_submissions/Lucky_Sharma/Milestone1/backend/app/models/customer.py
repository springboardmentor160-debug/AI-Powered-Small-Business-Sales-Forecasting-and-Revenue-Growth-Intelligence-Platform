from sqlalchemy import Column, Integer, String, Date

from app.database.database import Base


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(String(50), unique=True, index=True, nullable=False)
    customer_name = Column(String(150), nullable=False)
    email = Column(String(150), nullable=False)
    city = Column(String(100))
    registration_date = Column(Date)
