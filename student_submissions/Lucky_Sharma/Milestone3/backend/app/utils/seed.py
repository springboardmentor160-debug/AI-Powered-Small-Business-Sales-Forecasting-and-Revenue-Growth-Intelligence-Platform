from datetime import datetime
from pathlib import Path

import pandas as pd
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.customer import Customer
from app.models.inventory import Inventory
from app.models.product import Product
from app.models.sale import Sale
from app.models.user import User


BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data" / "processed"


def seed_database(db: Session):
    if db.query(User).count() == 0:
        demo_users = [
            ("Business Owner", "owner@marketmind.ai", "owner123", "business_owner"),
            ("Store Manager", "manager@marketmind.ai", "manager123", "store_manager"),
            ("Sales Executive", "sales@marketmind.ai", "sales123", "sales_executive"),
            ("Administrator", "admin@marketmind.ai", "admin123", "admin"),
        ]

        for name, email, password, role in demo_users:
            db.add(User(
                name=name,
                email=email,
                password_hash=hash_password(password),
                role=role,
            ))

    if db.query(Customer).count() == 0:
        df = pd.read_csv(DATA_DIR / "cleaned_customers.csv")
        for _, row in df.iterrows():
            registration = pd.to_datetime(
                row["registration_date"], errors="coerce"
            )
            db.add(Customer(
                customer_id=str(row["customer_id"]),
                customer_name=str(row["customer_name"]),
                email=str(row["email"]),
                city=str(row["city"]),
                registration_date=registration.date() if not pd.isna(registration) else None,
            ))

    if db.query(Product).count() == 0:
        df = pd.read_csv(DATA_DIR / "cleaned_products.csv")
        for _, row in df.iterrows():
            db.add(Product(
                product_id=str(row["product_id"]),
                product_name=str(row["product_name"]),
                category=str(row["category"]),
                unit_price=float(row["unit_price"]),
            ))

    db.commit()

    if db.query(Sale).count() == 0:
        df = pd.read_csv(DATA_DIR / "cleaned_sales.csv")
        for _, row in df.iterrows():
            db.add(Sale(
                order_id=str(row["order_id"]),
                order_date=pd.to_datetime(row["order_date"]).date(),
                product_id=str(row["product_id"]),
                product_name=str(row["product_name"]),
                customer_id=str(row["customer_id"]),
                quantity=float(row["quantity"]),
                unit_price=float(row["unit_price"]),
                revenue=float(row["revenue"]),
            ))

    if db.query(Inventory).count() == 0:
        df = pd.read_csv(DATA_DIR / "cleaned_inventory.csv")
        for _, row in df.iterrows():
            db.add(Inventory(
                product_id=str(row["product_id"]),
                product_name=str(row["product_name"]),
                category=str(row["category"]),
                stock_level=int(row["stock_level"]),
                reorder_point=int(row["reorder_point"]),
                unit_price=float(row["unit_price"]),
                warehouse=str(row["warehouse"]),
            ))

    db.commit()
