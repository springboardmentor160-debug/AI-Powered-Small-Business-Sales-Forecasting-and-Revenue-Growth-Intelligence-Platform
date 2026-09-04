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

if __name__ == "__main__":
    load_database()
