import os
import pandas as pd

RAW = "data/raw"
PROCESSED = "data/processed"

os.makedirs(PROCESSED, exist_ok=True)

sales = pd.read_csv(f"{RAW}/sales.csv")
customers = pd.read_csv(f"{RAW}/customers.csv")
products = pd.read_csv(f"{RAW}/products.csv")
inventory = pd.read_csv(f"{RAW}/inventory.csv")

# -------------------------
# Sales cleaning
# -------------------------
sales["order_date"] = pd.to_datetime(
    sales["order_date"], errors="coerce"
)

sales["quantity"] = pd.to_numeric(
    sales["quantity"], errors="coerce"
)

sales["unit_price"] = pd.to_numeric(
    sales["unit_price"], errors="coerce"
)

sales = sales.dropna(
    subset=["order_id", "order_date", "product_id", "customer_id", "quantity", "unit_price"]
)

sales = sales.drop_duplicates(subset=["order_id"])

sales = sales[
    (sales["quantity"] > 0) &
    (sales["unit_price"] > 0)
].copy()

sales["revenue"] = sales["quantity"] * sales["unit_price"]

sales["order_date"] = sales["order_date"].dt.date

# -------------------------
# Customer cleaning
# -------------------------
customers["email"] = (
    customers["email"]
    .astype(str)
    .str.strip()
    .str.lower()
)

customers = customers.drop_duplicates(subset=["email"])

customers["registration_date"] = pd.to_datetime(
    customers["registration_date"], errors="coerce"
).dt.date

# -------------------------
# Product cleaning
# -------------------------
products["product_name"] = (
    products["product_name"].astype(str).str.strip()
)

products["category"] = (
    products["category"].astype(str).str.strip()
)

products["unit_price"] = pd.to_numeric(
    products["unit_price"], errors="coerce"
)

products = products.dropna(subset=["product_id", "product_name", "unit_price"])
products = products[products["unit_price"] > 0]
products = products.drop_duplicates(subset=["product_id"])

# -------------------------
# Inventory cleaning
# -------------------------
inventory["stock_level"] = pd.to_numeric(
    inventory["stock_level"], errors="coerce"
)

inventory["reorder_point"] = pd.to_numeric(
    inventory["reorder_point"], errors="coerce"
)

inventory["stock_level"] = inventory["stock_level"].fillna(0)
inventory["reorder_point"] = inventory["reorder_point"].fillna(10)

inventory = inventory[inventory["stock_level"] >= 0]
inventory = inventory[inventory["reorder_point"] >= 0]

inventory = inventory.drop_duplicates(subset=["product_id"])

# -------------------------
# Save processed files
# -------------------------
sales.to_csv(f"{PROCESSED}/cleaned_sales.csv", index=False)
customers.to_csv(f"{PROCESSED}/cleaned_customers.csv", index=False)
products.to_csv(f"{PROCESSED}/cleaned_products.csv", index=False)
inventory.to_csv(f"{PROCESSED}/cleaned_inventory.csv", index=False)

print("\nData cleaning completed.")
print(f"Cleaned sales:      {len(sales)}")
print(f"Cleaned customers:  {len(customers)}")
print(f"Cleaned products:   {len(products)}")
print(f"Cleaned inventory:  {len(inventory)}")
print("\nSaved to data/processed/")
