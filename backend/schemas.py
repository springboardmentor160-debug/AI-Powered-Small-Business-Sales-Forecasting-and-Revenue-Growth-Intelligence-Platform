from datetime import date, datetime
from pydantic import BaseModel


class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    role_id: str


class UserOut(BaseModel):
    id: int
    name: str
    email: str

    class Config:
        from_attributes = True


class UserMeOut(BaseModel):
    id: int
    name: str
    email: str
    role: str

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    email: str
    password: str


class SalesTransactionOut(BaseModel):
    id: int
    store_id: str
    product_id: str
    sales_rep_id: int | None
    date: date
    units_sold: int
    inventory_level: int
    demand: float

    class Config:
        from_attributes = True


class TransactionOut(BaseModel):
    # Matches the rebuilt Transaction model, backed by
    # online_retail_prepped.csv (M2 segmentation dataset).
    id: int
    invoice_no: str
    stock_code: str
    description: str
    customer_id: str
    date: datetime
    quantity: int
    unit_price: float
    total_amount: float

    class Config:
        from_attributes = True