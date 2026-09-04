import csv
import random
from datetime import datetime, timedelta
import os

def generate_sample_data():
    raw_dir = os.path.join(os.path.dirname(__file__), "..", "..", "data", "raw")
    os.makedirs(raw_dir, exist_ok=True)
    raw_csv_path = os.path.join(raw_dir, "sales_inventory_raw.csv")

    categories = ["Electronics", "electronics", "Clothing", "Apparel & Accessories", "Home & Kitchen", "Groceries", "Books", "Beauty & Care"]
    products = [
        ("P101", "Wireless Noise-Canceling Headphones", "Electronics", 129.99, 45, 10),
        ("P102", "Ergonomic Office Chair", "Home & Kitchen", 199.50, 15, 5),
        ("P103", "Organic Cotton T-Shirt", "Clothing", 24.99, 120, 25),
        ("P104", "Stainless Steel Water Bottle", "Home & Kitchen", 18.00, 80, 20),
        ("P105", "Smart LED Desk Lamp", "Electronics", 39.99, 30, 8),
        ("P106", "Ceramic Coffee Mug Set", "Home & Kitchen", 29.95, 60, 15),
        ("P107", "Bluetooth Portable Speaker", "electronics", 49.99, 8, 12),  # low stock
        ("P108", "Running Shoes Pro", "Apparel & Accessories", 89.90, 22, 10),
        ("P109", "Gourmet Dark Chocolate Bar", "Groceries", 4.50, 200, 40),
        ("P110", "Mechanical Gaming Keyboard", "Electronics", 89.99, 5, 10),  # below reorder
        ("P111", "Hydrating Face Serum", "Beauty & Care", 34.50, 50, 15),
        ("P112", "Data Science Handbook", "Books", 42.00, 18, 5)
    ]

    stores = ["STORE-001", "STORE-002", "STORE-003"]
    customers = [f"CUST-{1000 + i}" for i in range(1, 26)] + ["", None] # include missing customer ids
    payment_methods = ["Credit Card", "credit card", "Cash", "cash", "UPI", "UPI / Mobile", "Debit Card", ""]

    start_date = datetime(2024, 1, 1)
    
    rows = []
    tx_id_counter = 10001

    for i in range(350):
        prod = random.choice(products)
        prod_id, prod_name, cat, price, stock, reorder = prod
        
        # Add random date within 60 days
        dt = start_date + timedelta(days=random.randint(0, 90), hours=random.randint(8, 20), minutes=random.randint(0, 59))
        
        # Mix date formats to simulate dirty raw data
        if i % 15 == 0:
            date_str = dt.strftime("%Y/%m/%d %H:%M")
        elif i % 20 == 0:
            date_str = dt.strftime("%d-%m-%Y %H:%M:%S")
        else:
            date_str = dt.strftime("%Y-%m-%d %H:%M:%S")
            
        qty = random.randint(1, 6)
        total = round(qty * price, 2)
        store = random.choice(stores)
        cust = random.choice(customers)
        pay_method = random.choice(payment_methods)

        rows.append({
            "transaction_id": f"TXN-{tx_id_counter}",
            "date": date_str,
            "product_id": prod_id,
            "product_name": prod_name,
            "category": cat,
            "quantity": qty,
            "unit_price": price,
            "total_amount": total,
            "store_id": store,
            "customer_id": cust if cust else "",
            "payment_method": pay_method,
            "stock_level": max(0, stock - random.randint(0, 10)),
            "reorder_threshold": reorder
        })
        
        tx_id_counter += 1

    # Inject deliberate duplicate rows for cleaning script to detect
    rows.append(rows[10].copy())
    rows.append(rows[25].copy())
    rows.append(rows[50].copy())

    headers = [
        "transaction_id", "date", "product_id", "product_name", "category",
        "quantity", "unit_price", "total_amount", "store_id", "customer_id",
        "payment_method", "stock_level", "reorder_threshold"
    ]

    with open(raw_csv_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Generated {len(rows)} raw transaction records at {raw_csv_path}")

if __name__ == "__main__":
    generate_sample_data()
