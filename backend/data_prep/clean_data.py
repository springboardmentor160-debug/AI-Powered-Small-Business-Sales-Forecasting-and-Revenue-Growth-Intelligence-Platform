import os
import csv
from datetime import datetime

def clean_dataset():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    raw_path = os.path.join(base_dir, "data", "raw", "sales_inventory_raw.csv")
    processed_dir = os.path.join(base_dir, "data", "processed")
    os.makedirs(processed_dir, exist_ok=True)

    if not os.path.exists(raw_path):
        raise FileNotFoundError(f"Raw data file not found at {raw_path}")

    print(f"Reading raw dataset from {raw_path}...")
    
    rows = []
    with open(raw_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)

    initial_count = len(rows)
    print(f"Initial raw rows: {initial_count}")

    # 1. Deduplication
    seen = set()
    unique_rows = []
    for r in rows:
        key = (r["transaction_id"], r["date"], r["product_id"], r["store_id"])
        if key not in seen:
            seen.add(key)
            unique_rows.append(r)

    print(f"Rows after removing duplicates: {len(unique_rows)} (Removed {initial_count - len(unique_rows)})")

    # 2. Category Normalization Map
    category_map = {
        "electronics": "Electronics",
        "Electronics": "Electronics",
        "Clothing": "Clothing",
        "Apparel & Accessories": "Clothing",
        "Home & Kitchen": "Home & Kitchen",
        "Groceries": "Groceries",
        "Books": "Books",
        "Beauty & Care": "Beauty & Care"
    }

    # 3. Clean and Transform Records
    cleaned_sales = []
    inventory_dict = {}

    for r in unique_rows:
        # Date parsing
        date_str = r.get("date", "").strip()
        parsed_date = None
        formats = [
            "%Y-%m-%d %H:%M:%S",
            "%Y/%m/%d %H:%M",
            "%d-%m-%Y %H:%M:%S",
            "%Y-%m-%d",
            "%Y/%m/%d"
        ]
        for fmt in formats:
            try:
                dt = datetime.strptime(date_str, fmt)
                parsed_date = dt.strftime("%Y-%m-%d %H:%M:%S")
                break
            except ValueError:
                continue
        if not parsed_date:
            parsed_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Category
        cat_raw = r.get("category", "").strip()
        cat_clean = category_map.get(cat_raw, cat_raw.title())

        # Customer ID
        cust_id = r.get("customer_id", "").strip()
        if not cust_id or cust_id.lower() in ["nan", "none", "null"]:
            cust_id = "GUEST"

        # Payment Method
        pay_raw = r.get("payment_method", "").strip().title()
        if not pay_raw or pay_raw.lower() in ["nan", "none"]:
            pay_clean = "Unknown"
        elif "Upi" in pay_raw:
            pay_clean = "UPI"
        elif "Credit" in pay_raw:
            pay_clean = "Credit Card"
        elif "Debit" in pay_raw:
            pay_clean = "Debit Card"
        elif "Cash" in pay_raw:
            pay_clean = "Cash"
        else:
            pay_clean = pay_raw

        # Quantities and Prices
        try:
            qty = max(1, int(float(r.get("quantity", 1))))
        except Exception:
            qty = 1

        try:
            price = max(0.0, float(r.get("unit_price", 0.0)))
        except Exception:
            price = 0.0

        total = round(qty * price, 2)

        try:
            stock = max(0, int(float(r.get("stock_level", 0))))
        except Exception:
            stock = 0

        try:
            reorder = max(0, int(float(r.get("reorder_threshold", 10))))
        except Exception:
            reorder = 10

        clean_row = {
            "transaction_id": r["transaction_id"],
            "date": parsed_date,
            "product_id": r["product_id"],
            "product_name": r["product_name"],
            "category": cat_clean,
            "quantity": qty,
            "unit_price": price,
            "total_amount": total,
            "store_id": r["store_id"],
            "customer_id": cust_id,
            "payment_method": pay_clean,
            "stock_level": stock,
            "reorder_threshold": reorder
        }
        cleaned_sales.append(clean_row)

        # Update Inventory lookup
        prod_id = r["product_id"]
        if prod_id not in inventory_dict:
            inventory_dict[prod_id] = {
                "product_id": prod_id,
                "product_name": r["product_name"],
                "category": cat_clean,
                "unit_price": price,
                "stock_level": stock,
                "reorder_threshold": reorder
            }

    # Write clean_sales.csv
    clean_sales_path = os.path.join(processed_dir, "clean_sales.csv")
    fieldnames_sales = [
        "transaction_id", "date", "product_id", "product_name", "category",
        "quantity", "unit_price", "total_amount", "store_id", "customer_id",
        "payment_method", "stock_level", "reorder_threshold"
    ]
    with open(clean_sales_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames_sales)
        writer.writeheader()
        writer.writerows(cleaned_sales)

    print(f"Saved cleaned sales data to {clean_sales_path} ({len(cleaned_sales)} rows)")

    # Write clean_inventory.csv
    clean_inventory_path = os.path.join(processed_dir, "clean_inventory.csv")
    fieldnames_inv = ["product_id", "product_name", "category", "unit_price", "stock_level", "reorder_threshold"]
    with open(clean_inventory_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames_inv)
        writer.writeheader()
        writer.writerows(inventory_dict.values())

    print(f"Saved cleaned inventory data to {clean_inventory_path} ({len(inventory_dict)} products)")

    return clean_sales_path, clean_inventory_path

if __name__ == "__main__":
    clean_dataset()
