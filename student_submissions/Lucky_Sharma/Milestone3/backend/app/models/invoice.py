from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey

from app.database.database import Base


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    sale_id = Column(Integer, ForeignKey("sales.id"), nullable=False)
    invoice_number = Column(String(80), unique=True, nullable=False)
    amount = Column(Float, nullable=False)
    payment_status = Column(String(30), default="Pending")
    invoice_date = Column(Date, nullable=False)
