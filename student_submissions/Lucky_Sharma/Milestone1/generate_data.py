import os
import random
from datetime import datetime, timedelta

import numpy as np
import pandas as pd

random.seed(42)
np.random.seed(42)

os.makedirs("data/raw", exist_ok=True)
os.makedirs("data/processed", exist_ok=True)

NUM_CUSTOMERS = 100
NUM_SALES = 2000

cities = [
    "Jaipur", "Delhi", "Mumbai", "Pune",
    "Ahmedabad", "Bangalore", "Hyderabad", "Chennai"
]

customers = []
for i in range(1, NUM_CUSTOMERS + 1):
    customers.append({
        "customer_id": f"CUST{i:04d}",
        "customer_name": f"Customer {i}",
        "email": f"customer{i}@example.com",
        "city": random.choice(cities),
        "registration_date": (
            datetime(2025, 1, 1)
            + timedelta(days=random.randint(0, 300))
        ).date(),
    })

customers_df = pd.DataFrame(customers)

product_data = [
    ("Laptop", "Electronics", 55000),
    ("Smartphone", "Electronics", 25000),
    ("Tablet", "Electronics", 18000),
    ("Monitor", "Electronics", 12000),
    ("Keyboard", "Accessories", 1800),
    ("Mouse", "Accessories", 900),
    ("Headphones", "Accessories", 2200),
    ("Webcam", "Accessories", 3500),
    ("USB Hub", "Accessories", 1200),
    ("Power Bank", "Accessories", 1800),
    ("Office Chair", "Furniture", 8500),
    ("Office Table", "Furniture", 12000),
    ("Bookshelf", "Furniture", 7000),
    ("Desk Lamp", "Furniture", 1800),
    ("Storage Cabinet", "Furniture", 9500),
    ("Printer", "Office Equipment", 15000),
    ("Scanner", "Office Equipment", 11000),
    ("Projector", "Office Equipment", 30000),
    ("Router", "Networking", 4500),
    ("WiFi Extender", "Networking", 2800),
    ("Notebook", "Stationery", 120),
    ("Pen Pack", "Stationery", 150),
    ("Marker Pack", "Stationery", 250),
    ("File Folder", "Stationery", 100),
    ("Calculator", "Stationery", 700),
    ("Coffee Maker", "Appliances", 6500),
    ("Electric Kettle", "Appliances", 2200),
    ("Microwave", "Appliances", 11000),
    ("Air Purifier", "Appliances", 15000),
    ("Vacuum Cleaner", "Appliances", 9000),
]

products = []
for i, (name, category, price) in enumerate(product_data, start=1):
    products.append({
        "product_id": f"PROD{i:03d}",
        "product_name": name,
        "category": category,
        "unit_price": price,
    })

products_df = pd.DataFrame(products)

sales = []
start_date = datetime(2025, 1, 1)
end_date = datetime(2025, 12, 31)

for i in range(1, NUM_SALES + 1):
    customer = random.choice(customers)
    product = random.choice(products)

    sale_date = start_date + timedelta(
        days=random.randint(0, (end_date - start_date).days)
    )

    sales.append({
        "order_id": f"ORD{i:05d}",
        "order_date": sale_date.date(),
        "product_id": product["product_id"],
        "product_name": product["product_name"],
        "customer_id": customer["customer_id"],
        "quantity": random.randint(1, 5),
        "unit_price": product["unit_price"],
    })

sales_df = pd.DataFrame(sales)

inventory = []
warehouses = ["Jaipur Warehouse", "Delhi Warehouse", "Mumbai Warehouse"]

for product in products:
    inventory.append({
        "product_id": product["product_id"],
        "product_name": product["product_name"],
        "category": product["category"],
        "stock_level": random.randint(2, 100),
        "reorder_point": random.randint(10, 30),
        "unit_price": product["unit_price"],
        "warehouse": random.choice(warehouses),
    })

inventory_df = pd.DataFrame(inventory)

# Intentional raw-data quality issues for Milestone 1 cleaning practice
sales_df.loc[10, "customer_id"] = np.nan
sales_df.loc[25, "quantity"] = np.nan
sales_df = pd.concat([sales_df, sales_df.iloc[[50]]], ignore_index=True)
inventory_df.loc[5, "stock_level"] = -10
customers_df = pd.concat([customers_df, customers_df.iloc[[10]]], ignore_index=True)

customers_df.to_csv("data/raw/customers.csv", index=False)
products_df.to_csv("data/raw/products.csv", index=False)
sales_df.to_csv("data/raw/sales.csv", index=False)
inventory_df.to_csv("data/raw/inventory.csv", index=False)

print("Raw datasets created successfully.")
print(f"Customers: {len(customers_df)}")
print(f"Products:  {len(products_df)}")
print(f"Sales:     {len(sales_df)}")
print(f"Inventory: {len(inventory_df)}")
