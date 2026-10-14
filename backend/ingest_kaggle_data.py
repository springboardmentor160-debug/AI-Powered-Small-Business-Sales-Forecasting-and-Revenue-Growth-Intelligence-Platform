"""
MarketMind AI — Kaggle Data Ingestion & Database Seeding CLI

Usage:
  python backend/ingest_kaggle_data.py --help
  python backend/ingest_kaggle_data.py --action download
  python backend/ingest_kaggle_data.py --action export --limit 5000
  python backend/ingest_kaggle_data.py --action seed --limit 500
  python backend/ingest_kaggle_data.py --action all --limit 1000
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
from sqlalchemy.orm import Session

from backend.database import SessionLocal, Base, engine
from backend.models import User, Customer, Product, Sale, Inventory, Invoice
from backend.auth import hash_password
from backend.kaggle_loader import (
    load_online_retail,
    load_retail_inventory,
    export_kaggle_datasets,
    download_dataset,
    DATASET_ONLINE_RETAIL_CSV,
    DATASET_RETAIL_INVENTORY,
    PROCESSED_DATA_DIR,
)

# Demo users to always ensure authentication works
DEMO_USERS = [
    {
        "name": "Business Owner",
        "email": "owner@marketmind.ai",
        "password": "password123",
        "role": "owner",
    },
    {
        "name": "Store Manager",
        "email": "manager@marketmind.ai",
        "password": "password123",
        "role": "manager",
    },
    {
        "name": "Sales Executive",
        "email": "exec@marketmind.ai",
        "password": "password123",
        "role": "sales_executive",
    },
    {
        "name": "System Administrator",
        "email": "admin@marketmind.ai",
        "password": "password123",
        "role": "admin",
    },
]


def seed_demo_users(session: Session):
    """Seed system demo accounts."""
    for u in DEMO_USERS:
        existing = session.query(User).filter(User.email == u["email"]).first()
        if not existing:
            user = User(
                name=u["name"],
                email=u["email"],
                password_hash=hash_password(u["password"]),
                role=u["role"],
            )
            session.add(user)
    session.commit()
    print("[DB Seed] Demo users ensured.")


def seed_kaggle_database(sales_limit: int = 500, inventory_limit: int = 200, wipe_existing: bool = False):
    """
    Seeds the SQLite database with authentic Kaggle records.
    - Online Retail -> Customers, Products, Sales, Invoices
    - Retail Store Inventory -> Inventory stock levels & reorder points
    """
    print(f"\n==================== SEEDING KAGGLE DATA (Limit: {sales_limit} sales) ====================")
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()

    try:
        if wipe_existing:
            print("[DB Seed] Wiping existing operational records (sales, invoices, inventory, products, customers)...")
            session.query(Invoice).delete()
            session.query(Sale).delete()
            session.query(Inventory).delete()
            session.query(Product).delete()
            session.query(Customer).delete()
            session.commit()

        # 1. Ensure Demo Users
        seed_demo_users(session)

        # 2. Load Cleaned Kaggle Data
        sales_csv = PROCESSED_DATA_DIR / "kaggle_clean_sales.csv"
        inv_csv = PROCESSED_DATA_DIR / "kaggle_clean_inventory.csv"

        if not sales_csv.exists() or not inv_csv.exists():
            print("[DB Seed] Processed Kaggle CSVs not found. Exporting fresh datasets...")
            export_kaggle_datasets(sales_sample_size=sales_limit * 3, inventory_sample_size=inventory_limit * 3)

        df_sales = pd.read_csv(sales_csv)
        df_inv = pd.read_csv(inv_csv)

        if len(df_sales) > sales_limit:
            df_sales = df_sales.head(sales_limit)

        # 3. Seed Customers
        print(f"\n[1/4] Seeding Customers from Kaggle Online Retail ({df_sales['customer_id'].nunique()} unique)...")
        for cust_id in df_sales["customer_id"].unique():
            existing = session.query(Customer).filter(Customer.id == str(cust_id)).first()
            if not existing:
                cust = Customer(
                    id=str(cust_id),
                    name=f"Client {cust_id}",
                    contact_info=f"contact_{cust_id.lower()}@retaildomain.com",
                )
                session.add(cust)
        session.commit()

        # 4. Seed Products
        print(f"\n[2/4] Seeding Products ({df_sales['product_name'].nunique()} unique catalog items)...")
        product_map = {}
        for _, row in df_sales[["product_name", "unit_price"]].drop_duplicates(subset=["product_name"]).iterrows():
            prod_name = str(row["product_name"])[:120]
            existing = session.query(Product).filter(Product.name == prod_name).first()
            if not existing:
                category = "General Retail"
                price = float(row["unit_price"])
                prod = Product(
                    name=prod_name,
                    category=category,
                    unit_price=price,
                )
                session.add(prod)
                session.flush()
                product_map[prod_name] = prod.id
            else:
                product_map[prod_name] = existing.id
        session.commit()

        # 5. Seed Sales & Invoices
        print(f"\n[3/4] Seeding Sales & Invoices ({len(df_sales)} transactions)...")
        sales_count = 0
        used_order_ids = set([s[0] for s in session.query(Sale.order_id).all()])

        for idx, row in df_sales.iterrows():
            raw_order_id = int(row["order_id"])
            order_id = raw_order_id
            if order_id in used_order_ids:
                order_id = 9000000 + idx
            used_order_ids.add(order_id)

            prod_id = product_map.get(str(row["product_name"])[:120])
            if not prod_id:
                continue

            sale_date = datetime.strptime(str(row["order_date"]), "%Y-%m-%d").date()
            sale = Sale(
                order_id=order_id,
                product_id=prod_id,
                customer_id=str(row["customer_id"]),
                quantity=int(row["quantity"]),
                unit_price=float(row["unit_price"]),
                sale_date=sale_date,
            )
            session.add(sale)
            session.flush()

            amount = round(int(row["quantity"]) * float(row["unit_price"]), 2)
            invoice = Invoice(
                sale_id=sale.id,
                amount=amount,
                payment_status="PAID",
            )
            session.add(invoice)
            sales_count += 1
        session.commit()

        # 6. Seed Inventory from Retail Store Inventory dataset
        print("\n[4/4] Seeding Inventory stock levels and reorder thresholds...")
        all_products = session.query(Product).all()
        inv_pool = df_inv.to_dict(orient="records")

        for idx, prod in enumerate(all_products):
            existing_inv = session.query(Inventory).filter(Inventory.product_id == prod.id).first()
            if not existing_inv:
                sample_inv = inv_pool[idx % len(inv_pool)] if inv_pool else {}
                stock_level = int(sample_inv.get("stock_level", 45))
                reorder_point = int(sample_inv.get("reorder_point", 30))
                # Update product category if available
                if "category" in sample_inv and prod.category == "General Retail":
                    prod.category = str(sample_inv["category"])

                inv = Inventory(
                    product_id=prod.id,
                    stock_level=stock_level,
                    reorder_point=reorder_point,
                )
                session.add(inv)
        session.commit()

        # Report summary
        print("\n========== DATABASE POPULATION COMPLETE ==========")
        print(f"Users in DB:      {session.query(User).count()}")
        print(f"Customers in DB:  {session.query(Customer).count()}")
        print(f"Products in DB:   {session.query(Product).count()}")
        print(f"Sales in DB:      {session.query(Sale).count()}")
        print(f"Inventory in DB:  {session.query(Inventory).count()}")
        print(f"Invoices in DB:   {session.query(Invoice).count()}")

        low_stock_count = session.query(Inventory).filter(Inventory.stock_level < Inventory.reorder_point).count()
        print(f"Low Stock Alerts: {low_stock_count}")

    except Exception as e:
        session.rollback()
        print(f"Error during Kaggle database seeding: {e}")
        raise
    finally:
        session.close()


def main():
    parser = argparse.ArgumentParser(description="MarketMind AI — Kaggle Data Ingestion CLI")
    parser.add_argument(
        "--action",
        choices=["download", "export", "seed", "all"],
        default="export",
        help="Action to perform: download, export CSVs, seed database, or all.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=2000,
        help="Number of records to sample / export / seed.",
    )
    parser.add_argument(
        "--wipe",
        action="store_true",
        help="Wipe existing records before seeding database.",
    )

    args = parser.parse_args()

    if args.action in ["download", "all"]:
        print("[Step 1] Downloading Kaggle datasets via kagglehub...")
        download_dataset(DATASET_ONLINE_RETAIL_CSV)
        download_dataset(DATASET_RETAIL_INVENTORY)

    if args.action in ["export", "all"]:
        print(f"[Step 2] Cleaning and exporting processed datasets (limit={args.limit})...")
        export_kaggle_datasets(sales_sample_size=args.limit, inventory_sample_size=args.limit)

    if args.action in ["seed", "all"]:
        print(f"[Step 3] Seeding SQLite database from Kaggle data (limit={args.limit})...")
        seed_kaggle_database(sales_limit=args.limit, wipe_existing=args.wipe)

    print("\n[Done] Kaggle ingestion completed successfully.")


if __name__ == "__main__":
    main()
