from datetime import datetime
from pathlib import Path
import pandas as pd
from backend.database import SessionLocal, Base, engine
from backend.models import User, Customer, Product, Sale, Inventory, Invoice
from backend.auth import hash_password

CSV_PATH = Path("data/processed/clean_sales_data.csv")

# Demo customer dictionary with realistic business names
CUSTOMER_METADATA = {
    "C001": {"name": "Acme Corporation", "contact_info": "purchasing@acme.com"},
    "C002": {"name": "Apex Retailers", "contact_info": "inventory@apexretail.com"},
    "C003": {"name": "Beta Enterprises", "contact_info": "contact@betaent.org"},
    "C004": {"name": "Delta LLC", "contact_info": "supplies@deltallc.net"},
    "C005": {"name": "Echo Supplies", "contact_info": "orders@echosupplies.io"},
}

# Product categories
PRODUCT_CATEGORIES = {
    "Notebook A": "Stationery",
    "Pen Set": "Writing Instruments",
    "Marker Box": "Stationery",
    "Stapler": "Office Equipment",
}

# Inventory baseline (with deliberate low-stock levels to demonstrate alerts)
INVENTORY_SEED = {
    "Notebook A": {"stock_level": 45, "reorder_point": 20},
    "Pen Set": {"stock_level": 10, "reorder_point": 15},     # Low stock alert: 10 < 15
    "Marker Box": {"stock_level": 6, "reorder_point": 12},     # Low stock alert: 6 < 12
    "Stapler": {"stock_level": 28, "reorder_point": 10},
}

# Demo accounts required by Milestone 1 specification
DEMO_USERS = [
    {
        "name": "Business Owner",
        "email": "owner@marketmind.ai",
        "username_alias": "owner",
        "password": "password123",
        "role": "owner",
    },
    {
        "name": "Store Manager",
        "email": "manager@marketmind.ai",
        "username_alias": "manager",
        "password": "password123",
        "role": "manager",
    },
    {
        "name": "Sales Executive",
        "email": "exec@marketmind.ai",
        "username_alias": "exec",
        "password": "password123",
        "role": "sales_executive",
    },
    {
        "name": "System Administrator",
        "email": "admin@marketmind.ai",
        "username_alias": "admin",
        "password": "password123",
        "role": "admin",
    },
]


def load_data():
    print("Beginning idempotent database loading...")

    # Ensure tables exist
    Base.metadata.create_all(bind=engine)

    if not CSV_PATH.exists():
        raise FileNotFoundError(f"Cleaned CSV dataset not found at {CSV_PATH}. Run backend/data_cleaning.py first.")

    df = pd.read_csv(CSV_PATH)
    session = SessionLocal()

    try:
        # 1. Seed Users
        print("\n[1/5] Seeding demo users...")
        for user_data in DEMO_USERS:
            existing_user = session.query(User).filter(User.email == user_data["email"]).first()
            if not existing_user:
                new_user = User(
                    name=user_data["name"],
                    email=user_data["email"],
                    password_hash=hash_password(user_data["password"]),
                    role=user_data["role"],
                )
                session.add(new_user)
                print(f"  + Added user: {user_data['name']} ({user_data['email']}, role={user_data['role']})")
            else:
                print(f"  = User already exists: {user_data['email']}")
        session.commit()

        # 2. Seed Customers
        print("\n[2/5] Seeding customers...")
        for cust_id in df["customer_id"].unique():
            existing_cust = session.query(Customer).filter(Customer.id == cust_id).first()
            if not existing_cust:
                meta = CUSTOMER_METADATA.get(cust_id, {"name": f"Customer {cust_id}", "contact_info": None})
                cust = Customer(id=cust_id, name=meta["name"], contact_info=meta["contact_info"])
                session.add(cust)
                print(f"  + Added customer: {cust_id} ({meta['name']})")
            else:
                print(f"  = Customer already exists: {cust_id}")
        session.commit()

        # 3. Seed Products
        print("\n[3/5] Seeding products...")
        product_map = {}
        for _, row in df[["product_name", "unit_price"]].drop_duplicates().iterrows():
            prod_name = row["product_name"]
            existing_prod = session.query(Product).filter(Product.name == prod_name).first()
            if not existing_prod:
                prod = Product(
                    name=prod_name,
                    category=PRODUCT_CATEGORIES.get(prod_name, "General"),
                    unit_price=float(row["unit_price"]),
                )
                session.add(prod)
                session.flush()
                product_map[prod_name] = prod.id
                print(f"  + Added product: {prod_name} ($ {row['unit_price']})")
            else:
                product_map[prod_name] = existing_prod.id
                print(f"  = Product already exists: {prod_name}")
        session.commit()

        # 4. Seed Sales and Invoices
        print("\n[4/5] Seeding sales and invoices (from cleaned data)...")
        sales_added = 0
        for _, row in df.iterrows():
            order_id = int(row["order_id"])
            existing_sale = session.query(Sale).filter(Sale.order_id == order_id).first()
            if not existing_sale:
                prod_id = product_map.get(row["product_name"])
                if not prod_id:
                    prod = session.query(Product).filter(Product.name == row["product_name"]).first()
                    prod_id = prod.id

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

                # Generate invoice
                amount = round(int(row["quantity"]) * float(row["unit_price"]), 2)
                invoice = Invoice(
                    sale_id=sale.id,
                    amount=amount,
                    payment_status="PAID",
                )
                session.add(invoice)
                sales_added += 1
                print(f"  + Added sale order #{order_id}: {row['product_name']} x {int(row['quantity'])} -> ${amount}")
            else:
                print(f"  = Sale already exists for order #{order_id}")
        session.commit()

        # 5. Seed Inventory
        print("\n[5/5] Seeding inventory...")
        all_products = session.query(Product).all()
        for prod in all_products:
            existing_inv = session.query(Inventory).filter(Inventory.product_id == prod.id).first()
            inv_defaults = INVENTORY_SEED.get(prod.name, {"stock_level": 50, "reorder_point": 10})
            if not existing_inv:
                inv = Inventory(
                    product_id=prod.id,
                    stock_level=inv_defaults["stock_level"],
                    reorder_point=inv_defaults["reorder_point"],
                )
                session.add(inv)
                status = "ALERT (LOW STOCK)" if inv.is_low_stock else "OK"
                print(f"  + Added inventory for {prod.name}: Stock={inv.stock_level}, Reorder={inv.reorder_point} [{status}]")
            else:
                print(f"  = Inventory already exists for product: {prod.name}")
        session.commit()

        # Final Verification
        user_count = session.query(User).count()
        cust_count = session.query(Customer).count()
        prod_count = session.query(Product).count()
        sale_count = session.query(Sale).count()
        inv_count = session.query(Inventory).count()
        invc_count = session.query(Invoice).count()

        print("\n========== SEEDING COMPLETE ==========")
        print(f"Users in DB:      {user_count}")
        print(f"Customers in DB:  {cust_count}")
        print(f"Products in DB:   {prod_count}")
        print(f"Sales in DB:      {sale_count} (Must be exactly 8)")
        print(f"Inventory in DB:  {inv_count}")
        print(f"Invoices in DB:   {invc_count}")

        if sale_count != 8:
            print(f"WARNING: Expected 8 sales records, but found {sale_count}!")

    except Exception as e:
        session.rollback()
        print("Error during data seeding:", e)
        raise
    finally:
        session.close()


if __name__ == "__main__":
    load_data()