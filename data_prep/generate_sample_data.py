"""Generate reproducible synthetic raw datasets for MarketMind AI Milestone 1."""

from pathlib import Path

import numpy as np
import pandas as pd

SEED = 20260928
START_DATE = "2023-01-01"
END_DATE = "2025-12-31"

BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = BASE_DIR / "data" / "raw"


PRODUCTS = [
    ("P001", "Notebook", "Stationery", 8.50),
    ("P002", "Ballpoint Pen Pack", "Stationery", 5.25),
    ("P003", "Desk Organizer", "Stationery", 14.00),
    ("P004", "Printer Paper", "Stationery", 6.75),
    ("P005", "Wireless Mouse", "Electronics", 24.99),
    ("P006", "USB-C Hub", "Electronics", 34.50),
    ("P007", "Bluetooth Speaker", "Electronics", 49.99),
    ("P008", "Webcam", "Electronics", 59.00),
    ("P009", "Coffee Beans", "Food and Beverage", 15.50),
    ("P010", "Tea Assortment", "Food and Beverage", 12.75),
    ("P011", "Reusable Water Bottle", "Food and Beverage", 18.00),
    ("P012", "Snack Box", "Food and Beverage", 22.50),
    ("P013", "Hand Soap", "Household", 4.75),
    ("P014", "Cleaning Spray", "Household", 7.25),
    ("P015", "Storage Basket", "Household", 16.50),
    ("P016", "LED Bulb Pack", "Household", 11.99),
    ("P017", "Cotton T-Shirt", "Apparel", 19.99),
    ("P018", "Canvas Tote Bag", "Apparel", 13.50),
    ("P019", "Baseball Cap", "Apparel", 16.00),
    ("P020", "Running Socks", "Apparel", 9.99),
    ("P021", "Garden Gloves", "Outdoor", 8.99),
    ("P022", "Plant Pot", "Outdoor", 12.00),
    ("P023", "Hand Trowel", "Outdoor", 10.50),
    ("P024", "Watering Can", "Outdoor", 21.00),
]

CITIES = ["Bengaluru", "Chennai", "Delhi", "Hyderabad", "Kolkata", "Mumbai", "Pune"]
STORES = ["S001", "S002", "S003", "S004"]
PAYMENT_METHODS = ["Card", "Cash", "UPI", "Bank Transfer"]


def build_customers(rng: np.random.Generator) -> pd.DataFrame:
    customer_count = 300
    first_names = [
        "Aarav", "Ananya", "Arjun", "Diya", "Ishaan", "Kavya", "Neha", "Rohan",
        "Saanvi", "Vikram", "Meera", "Aditya", "Nisha", "Rahul", "Tara",
    ]
    last_names = [
        "Sharma", "Patel", "Iyer", "Reddy", "Gupta", "Nair", "Singh", "Joshi",
        "Das", "Mehta", "Khan", "Pillai",
    ]

    names = [
        f"{rng.choice(first_names)} {rng.choice(last_names)}"
        for _ in range(customer_count)
    ]
    registration_dates = pd.to_datetime(
        rng.integers(
            pd.Timestamp("2021-01-01").value // 86_400_000_000_000,
            pd.Timestamp("2024-12-31").value // 86_400_000_000_000,
            size=customer_count,
        ),
        unit="D",
    )

    customers = pd.DataFrame(
        {
            "customer_id": [f"C{number:04d}" for number in range(1, customer_count + 1)],
            "name": names,
            "email": [f"customer{number:04d}@example.com" for number in range(1, customer_count + 1)],
            "gender": rng.choice(["Female", "Male", "Non-binary"], size=customer_count, p=[0.47, 0.48, 0.05]),
            "age": rng.integers(18, 71, size=customer_count),
            "city": rng.choice(CITIES, size=customer_count),
            "registration_date": registration_dates.strftime("%Y-%m-%d"),
        }
    )
    return customers


def build_inventory() -> pd.DataFrame:
    inventory_rows = []
    for product_id, product_name, category, _ in PRODUCTS:
        for store_id in STORES:
            inventory_rows.append(
                {
                    "product_id": product_id,
                    "product_name": product_name,
                    "category": category,
                    "stock_level": 20 + (int(product_id[1:]) * 7 + int(store_id[3:]) * 11) % 181,
                    "reorder_threshold": 15 + (int(product_id[1:]) * 3 + int(store_id[3:]) * 5) % 36,
                    "store_id": store_id,
                }
            )
    return pd.DataFrame(inventory_rows)


def build_sales(rng: np.random.Generator, customers: pd.DataFrame) -> pd.DataFrame:
    transaction_count = 12_000
    dates = pd.date_range(START_DATE, END_DATE, freq="D")
    day_weights = np.ones(len(dates), dtype=float)
    day_weights += np.where(dates.dayofweek >= 5, 0.18, 0.0)
    day_weights += np.where(dates.month.isin([10, 11, 12]), 0.12, 0.0)

    product_weights = np.array([
        0.055, 0.05, 0.035, 0.045, 0.06, 0.045, 0.035, 0.03,
        0.05, 0.04, 0.03, 0.025, 0.045, 0.04, 0.035, 0.04,
        0.045, 0.035, 0.03, 0.04, 0.035, 0.03, 0.025, 0.035,
    ])
    product_indices = rng.choice(
        len(PRODUCTS), size=transaction_count, p=product_weights / product_weights.sum()
    )
    customer_indices = rng.choice(len(customers), size=transaction_count)
    selected_dates = rng.choice(dates, size=transaction_count, p=day_weights / day_weights.sum())
    quantities = rng.choice([1, 2, 3, 4, 5, 6], size=transaction_count, p=[0.34, 0.28, 0.18, 0.11, 0.06, 0.03])
    store_ids = rng.choice(STORES, size=transaction_count, p=[0.32, 0.25, 0.23, 0.20])

    rows = []
    for number, (product_index, customer_index, sale_date, quantity, store_id) in enumerate(
        zip(product_indices, customer_indices, selected_dates, quantities, store_ids),
        start=1,
    ):
        product_id, product_name, category, base_price = PRODUCTS[product_index]
        unit_price = round(base_price * rng.uniform(0.94, 1.06), 2)
        rows.append(
            {
                "transaction_id": f"T{number:06d}",
                "date": pd.Timestamp(sale_date).strftime("%Y-%m-%d"),
                "product_id": product_id,
                "product_name": product_name,
                "category": category,
                "quantity": int(quantity),
                "unit_price": unit_price,
                "total_amount": round(int(quantity) * unit_price, 2),
                "store_id": store_id,
                "customer_id": customers.iloc[customer_index]["customer_id"],
                "payment_method": rng.choice(PAYMENT_METHODS, p=[0.42, 0.18, 0.32, 0.08]),
            }
        )
    return pd.DataFrame(rows)


def generate_datasets() -> None:
    rng = np.random.default_rng(SEED)
    customers = build_customers(rng)
    inventory = build_inventory()
    sales = build_sales(rng, customers)

    (RAW_DIR / "sales").mkdir(parents=True, exist_ok=True)
    (RAW_DIR / "inventory").mkdir(parents=True, exist_ok=True)
    (RAW_DIR / "customers").mkdir(parents=True, exist_ok=True)

    sales.to_csv(RAW_DIR / "sales" / "sales.csv", index=False)
    inventory.to_csv(RAW_DIR / "inventory" / "inventory.csv", index=False)
    customers.to_csv(RAW_DIR / "customers" / "customers.csv", index=False)

    print(f"Generated {len(sales):,} sales rows.")
    print(f"Generated {len(inventory):,} inventory rows.")
    print(f"Generated {len(customers):,} customer rows.")


if __name__ == "__main__":
    generate_datasets()
