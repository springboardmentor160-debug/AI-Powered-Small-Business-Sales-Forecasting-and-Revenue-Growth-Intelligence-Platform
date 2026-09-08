import csv
import random
from datetime import datetime, timedelta
import os


def generate_sample_data():
    raw_dir = os.path.join(os.path.dirname(__file__), "..", "..", "data", "raw")
    os.makedirs(raw_dir, exist_ok=True)
    raw_csv_path = os.path.join(raw_dir, "orders_raw.csv")

    menu_items = [
        ("M101", "Paneer Tikka Skewers", "Starters", 249.00, 40, 10),
        ("M102", "Peri-Peri Fries", "Sides", 129.00, 90, 20),
        ("M103", "Butter Chicken Bowl", "Main Course", 329.00, 35, 8),
        ("M104", "Margherita Wood-Fired Pizza", "Main Course", 299.00, 25, 8),
        ("M105", "Mango Basil Cooler", "Beverages", 149.00, 70, 15),
        ("M106", "Choco Lava Cake", "Desserts", 179.00, 8, 12),        # low stock
        ("M107", "Veg Hakka Noodles", "Main Course", 219.00, 45, 10),
        ("M108", "Cold Brew Coffee", "beverages", 159.00, 60, 15),
        ("M109", "Loaded Nachos Platter", "starters", 269.00, 5, 10), # below reorder
        ("M110", "Classic Cheese Burger", "Main Course", 239.00, 30, 8),
        ("M111", "Falafel Wrap", "Sides", 189.00, 22, 8),
        ("M112", "Blueberry Cheesecake", "Desserts", 199.00, 15, 6),
    ]

    outlets = ["OUT-BBSR", "OUT-KOL", "OUT-BLR"]
    patrons = [f"PAT-{2000 + i}" for i in range(1, 26)] + ["", None]  # some missing patron ids
    payment_modes = ["UPI", "upi", "Card", "card", "Cash", "cash", "Wallet", ""]

    start_date = datetime(2025, 1, 1)
    rows = []
    order_counter = 50001

    for i in range(350):
        item = random.choice(menu_items)
        item_id, item_name, cat, price, stock, reorder = item

        dt = start_date + timedelta(days=random.randint(0, 90), hours=random.randint(8, 22), minutes=random.randint(0, 59))

        if i % 15 == 0:
            time_str = dt.strftime("%Y/%m/%d %H:%M")
        elif i % 20 == 0:
            time_str = dt.strftime("%d-%m-%Y %H:%M:%S")
        else:
            time_str = dt.strftime("%Y-%m-%d %H:%M:%S")

        qty = random.randint(1, 5)
        total = round(qty * price, 2)
        outlet = random.choice(outlets)
        patron = random.choice(patrons)
        pay_mode = random.choice(payment_modes)

        rows.append({
            "order_id": f"ORD-{order_counter}",
            "order_time": time_str,
            "item_id": item_id,
            "item_name": item_name,
            "category": cat,
            "unit_price": price,
            "quantity": qty,
            "total_amount": total,
            "outlet_id": outlet,
            "patron_id": patron,
            "payment_mode": pay_mode,
            "stock_units": stock,
            "reorder_level": reorder,
        })
        order_counter += 1

    fieldnames = list(rows[0].keys())
    with open(raw_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Generated {len(rows)} raw (dirty) order rows -> {raw_csv_path}")


if __name__ == "__main__":
    generate_sample_data()
