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

from datetime import date

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
    id: int
    customer_id: str
    date: date
    product_category: str
    quantity: int
    price_per_unit: float
    total_amount: float

    class Config:
        from_attributes = True