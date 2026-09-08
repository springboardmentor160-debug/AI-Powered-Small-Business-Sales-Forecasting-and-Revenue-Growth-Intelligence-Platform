import csv
import os
from datetime import datetime

CATEGORY_MAP = {
    "starters": "Starters",
    "sides": "Sides",
    "main course": "Main Course",
    "beverages": "Beverages",
    "desserts": "Desserts",
}

PAYMENT_MAP = {
    "upi": "UPI",
    "card": "Card",
    "cash": "Cash",
    "wallet": "Wallet",
}

DATE_FORMATS = ["%Y-%m-%d %H:%M:%S", "%Y/%m/%d %H:%M", "%d-%m-%Y %H:%M:%S"]


def parse_datetime(raw_value: str):
    raw_value = (raw_value or "").strip()
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(raw_value, fmt)
        except ValueError:
            continue
    return None


def normalize_category(raw_value: str) -> str:
    key = (raw_value or "").strip().lower()
    return CATEGORY_MAP.get(key, (raw_value or "Uncategorized").strip().title())


def normalize_payment(raw_value: str) -> str:
    key = (raw_value or "").strip().lower()
    return PAYMENT_MAP.get(key, "Unknown")


def clean():
    raw_dir = os.path.join(os.path.dirname(__file__), "..", "..", "data", "raw")
    processed_dir = os.path.join(os.path.dirname(__file__), "..", "..", "data", "processed")
    os.makedirs(processed_dir, exist_ok=True)

    raw_path = os.path.join(raw_dir, "orders_raw.csv")
    orders_out_path = os.path.join(processed_dir, "orders_clean.csv")
    menu_out_path = os.path.join(processed_dir, "menu_clean.csv")

    menu_seen = {}
    clean_rows = []
    dropped = 0

    with open(raw_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            dt = parse_datetime(row.get("order_time", ""))
            patron_id = (row.get("patron_id") or "").strip() or "WALKIN"
            qty_raw = row.get("quantity", "").strip()

            if dt is None or not qty_raw:
                dropped += 1
                continue

            category = normalize_category(row.get("category", ""))
            payment_mode = normalize_payment(row.get("payment_mode", ""))
            qty = int(qty_raw)
            unit_price = float(row["unit_price"])
            total_amount = round(qty * unit_price, 2)

            clean_rows.append({
                "order_id": row["order_id"],
                "order_time": dt.strftime("%Y-%m-%d %H:%M:%S"),
                "item_id": row["item_id"],
                "quantity": qty,
                "unit_price": unit_price,
                "total_amount": total_amount,
                "outlet_id": row["outlet_id"],
                "patron_id": patron_id,
                "payment_mode": payment_mode,
            })

            item_id = row["item_id"]
            if item_id not in menu_seen:
                menu_seen[item_id] = {
                    "item_id": item_id,
                    "item_name": row["item_name"],
                    "category": category,
                    "unit_price": unit_price,
                    "stock_units": int(row["stock_units"]),
                    "reorder_level": int(row["reorder_level"]),
                }

    with open(orders_out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(clean_rows[0].keys()))
        writer.writeheader()
        writer.writerows(clean_rows)

    with open(menu_out_path, "w", newline="", encoding="utf-8") as f:
        menu_rows = list(menu_seen.values())
        writer = csv.DictWriter(f, fieldnames=list(menu_rows[0].keys()))
        writer.writeheader()
        writer.writerows(menu_rows)

    print(f"Cleaned {len(clean_rows)} orders ({dropped} dropped) -> {orders_out_path}")
    print(f"Extracted {len(menu_seen)} unique menu items -> {menu_out_path}")


if __name__ == "__main__":
    clean()
