import os
import csv
import sqlite3

def load_database():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    schema_path = os.path.join(base_dir, "db", "schema.sql")
    db_path = os.path.join(base_dir, "db", "marketmind.db")
    clean_sales_path = os.path.join(base_dir, "data", "processed", "clean_sales.csv")

    if not os.path.exists(schema_path):
        raise FileNotFoundError(f"Schema file not found at {schema_path}")
    if not os.path.exists(clean_sales_path):
        raise FileNotFoundError(f"Clean sales dataset not found at {clean_sales_path}. Run clean_data.py first.")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Read and execute schema
    print(f"Applying SQL schema from {schema_path}...")
    with open(schema_path, "r", encoding="utf-8") as f:
        schema_sql = f.read()
    cursor.executescript(schema_sql)

    # 1. Seed Roles
    print("Seeding system roles...")
    roles_data = [
        (1, "business_owner", "Full access to executive analytics, revenue reports, and all store locations"),
        (2, "store_manager", "Access to store inventory, stock replenishment alerts, and store daily metrics"),
        (3, "sales_executive", "Access to personal sales processing and store transaction history"),
        (4, "administrator", "Access to user administration, role assignment, and audit logs")
    ]
    cursor.executemany("INSERT OR REPLACE INTO roles (role_id, role_name, description) VALUES (?, ?, ?);", roles_data)

    # 2. Seed Stores
    print("Seeding stores...")
    stores_data = [
        ("STORE-001", "Downtown Flagship Store", "100 Main St, New York, NY", "+1-212-555-0101"),
        ("STORE-002", "Uptown Outlet", "450 5th Ave, New York, NY", "+1-212-555-0102"),
        ("STORE-003", "Metro Mall Branch", "800 Broadway, Brooklyn, NY", "+1-718-555-0103")
    ]
    cursor.executemany("INSERT OR REPLACE INTO stores (store_id, store_name, location, contact_phone) VALUES (?, ?, ?, ?);", stores_data)

    # 3. Read Clean Sales CSV
    sales_rows = []
    with open(clean_sales_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            sales_rows.append(r)

    # 4. Populate Inventory Table
    print("Populating inventory table...")
    inventory_dict = {}
    for row in sales_rows:
        pid = row["product_id"]
        if pid not in inventory_dict:
            inventory_dict[pid] = (
                pid,
                row["product_name"],
                row["category"],
                float(row["unit_price"]),
                int(row["stock_level"]),
                int(row["reorder_threshold"])
            )
    cursor.executemany("""
        INSERT OR REPLACE INTO inventory (product_id, product_name, category, unit_price, stock_level, reorder_threshold)
        VALUES (?, ?, ?, ?, ?, ?);
    """, list(inventory_dict.values()))

    # 5. Populate Customers Table
    print("Populating customers table...")
    cust_dict = {}
    for row in sales_rows:
        cust = row["customer_id"].strip()
        if cust and cust != "GUEST" and cust not in cust_dict:
            cust_dict[cust] = (cust, f"Customer {cust.replace('CUST-', '')}", f"{cust.lower()}@example.com", "+1-555-0199")
    
    cust_dict["GUEST"] = ("GUEST", "Guest Customer (Walk-in)", "guest@marketmind.ai", "N/A")
    cursor.executemany("INSERT OR REPLACE INTO customers (customer_id, customer_name, email, phone) VALUES (?, ?, ?, ?);", list(cust_dict.values()))

    # 6. Populate Transactions Table
    print("Populating transactions table...")
    tx_records = []
    for row in sales_rows:
        tx_records.append((
            row["transaction_id"],
            row["date"],
            row["product_id"],
            int(row["quantity"]),
            float(row["unit_price"]),
            float(row["total_amount"]),
            row["store_id"],
            row["customer_id"],
            row["payment_method"]
        ))
    cursor.executemany("""
        INSERT OR REPLACE INTO transactions 
        (transaction_id, transaction_date, product_id, quantity, unit_price, total_amount, store_id, customer_id, payment_method)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, tx_records)

    # 7. Seed Initial Demo Users
    print("Seeding default demo users...")
    demo_users = [
        ("owner", "owner@marketmind.ai", "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeg6Lruj3vjPGga31lW", "Alice Owner (CEO)", 1, "STORE-001"),
        ("manager", "manager@marketmind.ai", "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeg6Lruj3vjPGga31lW", "Bob Manager", 2, "STORE-001"),
        ("exec", "exec@marketmind.ai", "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeg6Lruj3vjPGga31lW", "Charlie Sales Exec", 3, "STORE-001"),
        ("admin", "admin@marketmind.ai", "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeg6Lruj3vjPGga31lW", "Diana Admin", 4, "STORE-001")
    ]
    cursor.executemany("""
        INSERT OR REPLACE INTO users (username, email, hashed_password, full_name, role_id, store_id)
        VALUES (?, ?, ?, ?, ?, ?);
    """, demo_users)

    conn.commit()
    conn.close()
    print(f"Database successfully loaded and initialized at {db_path}!")

def seed_database_orm():
    """
    Database-agnostic seeder using SQLAlchemy ORM.
    Works seamlessly on SQLite and Supabase PostgreSQL.
    """
    import sys
    backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    if backend_dir not in sys.path:
        sys.path.insert(0, backend_dir)
    
    from database import SessionLocal, engine, Base
    import models
    from datetime import datetime

    # 1. Create tables if not present
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        if db.query(models.Role).first():
            print("[Database Seeder] Database is already initialized.")
            return

        print("[Database Seeder] Seeding initial roles...")
        roles_data = [
            models.Role(role_id=1, role_name="business_owner", description="Full access to executive analytics, revenue reports, and all store locations"),
            models.Role(role_id=2, role_name="store_manager", description="Access to store inventory, stock replenishment alerts, and store daily metrics"),
            models.Role(role_id=3, role_name="sales_executive", description="Access to personal sales processing and store transaction history"),
            models.Role(role_id=4, role_name="administrator", description="Access to user administration, role assignment, and audit logs")
        ]
        db.add_all(roles_data)
        db.commit()

        print("[Database Seeder] Seeding stores...")
        stores_data = [
            models.Store(store_id="STORE-001", store_name="Downtown Flagship Store", location="100 Main St, New York, NY", contact_phone="+1-212-555-0101"),
            models.Store(store_id="STORE-002", store_name="Uptown Outlet", location="450 5th Ave, New York, NY", contact_phone="+1-212-555-0102"),
            models.Store(store_id="STORE-003", store_name="Metro Mall Branch", location="800 Broadway, Brooklyn, NY", contact_phone="+1-718-555-0103")
        ]
        db.add_all(stores_data)
        db.commit()

        print("[Database Seeder] Seeding demo users...")
        demo_users = [
            models.User(username="owner", email="owner@marketmind.ai", hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeg6Lruj3vjPGga31lW", full_name="Alice Owner (CEO)", role_id=1, store_id="STORE-001"),
            models.User(username="manager", email="manager@marketmind.ai", hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeg6Lruj3vjPGga31lW", full_name="Bob Manager", role_id=2, store_id="STORE-001"),
            models.User(username="exec", email="exec@marketmind.ai", hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeg6Lruj3vjPGga31lW", full_name="Charlie Sales Exec", role_id=3, store_id="STORE-001"),
            models.User(username="admin", email="admin@marketmind.ai", hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeg6Lruj3vjPGga31lW", full_name="Diana Admin", role_id=4, store_id="STORE-001")
        ]
        db.add_all(demo_users)
        db.commit()

        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        clean_sales_path = os.path.join(base_dir, "data", "processed", "clean_sales.csv")
        if not os.path.exists(clean_sales_path):
            clean_sales_path = os.path.join(base_dir, "cleaned_sales_data.csv")

        if os.path.exists(clean_sales_path):
            print(f"[Database Seeder] Seeding inventory and transactions from {clean_sales_path}...")
            with open(clean_sales_path, mode="r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                sales_rows = list(reader)

            inv_dict = {}
            for r in sales_rows:
                pid = r.get("product_id")
                if pid and pid not in inv_dict:
                    inv_dict[pid] = models.Inventory(
                        product_id=pid,
                        product_name=r.get("product_name", f"Product {pid}"),
                        category=r.get("category", "General"),
                        unit_price=float(r.get("unit_price", 10.0)),
                        stock_level=int(r.get("stock_level", 50)),
                        reorder_threshold=int(r.get("reorder_threshold", 10))
                    )
            db.add_all(list(inv_dict.values()))
            db.commit()

            cust_dict = {
                "GUEST": models.Customer(customer_id="GUEST", customer_name="Guest Customer (Walk-in)", email="guest@marketmind.ai", phone="N/A")
            }
            for r in sales_rows:
                cid = (r.get("customer_id") or "").strip()
                if cid and cid != "GUEST" and cid not in cust_dict:
                    cust_dict[cid] = models.Customer(
                        customer_id=cid,
                        customer_name=f"Customer {cid.replace('CUST-', '')}",
                        email=f"{cid.lower()}@example.com",
                        phone="+1-555-0199"
                    )
            db.add_all(list(cust_dict.values()))
            db.commit()

            tx_objs = []
            for r in sales_rows:
                date_str = r.get("date") or r.get("transaction_date")
                try:
                    dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S") if " " in str(date_str) else datetime.strptime(str(date_str), "%Y-%m-%d")
                except Exception:
                    dt = datetime.utcnow()

                tx_objs.append(models.Transaction(
                    transaction_id=r.get("transaction_id"),
                    transaction_date=dt,
                    product_id=r.get("product_id"),
                    quantity=int(r.get("quantity", 1)),
                    unit_price=float(r.get("unit_price", 10.0)),
                    total_amount=float(r.get("total_amount", 10.0)),
                    store_id=r.get("store_id", "STORE-001"),
                    customer_id=r.get("customer_id", "GUEST"),
                    payment_method=r.get("payment_method", "Cash")
                ))
            db.add_all(tx_objs)
            db.commit()
            print(f"[Database Seeder] Successfully seeded {len(tx_objs)} transactions!")

    except Exception as e:
        db.rollback()
        print(f"[Database Seeder] Error during ORM seed: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    if os.getenv("DATABASE_URL"):
        seed_database_orm()
    else:
        load_database()
