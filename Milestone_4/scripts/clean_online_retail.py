"""
MarketMind AI — Data Cleaning Script
Cleans the Online Retail II dataset and generates a synthetic Inventory table.

Usage:
    python clean_online_retail.py

Expects the raw file at ./online_retail_II.csv (rename your downloaded file,
or update RAW_PATH below).
"""

import pandas as pd
import numpy as np

RAW_PATH = "online_retail_II.csv"   # update to your actual filename
OUT_DIR = "cleaned_data"

import os
os.makedirs(OUT_DIR, exist_ok=True)

# ---------------------------------------------------------
# 1. Load
# ---------------------------------------------------------
df = pd.read_csv(RAW_PATH, encoding="ISO-8859-1")  # this dataset often has non-UTF8 chars

print(f"Raw rows: {len(df)}")

# Standardize column names (in case of trailing spaces / case differences)
df.columns = [c.strip() for c in df.columns]
df = df.rename(columns={"Customer ID": "CustomerID"})

# ---------------------------------------------------------
# 2. Handle cancellations / returns
# ---------------------------------------------------------
# Invoices starting with 'C' are cancellations
df["is_cancelled"] = df["Invoice"].astype(str).str.startswith("C")

# Keep a separate cancellations table (useful later for anomaly detection)
cancellations = df[df["is_cancelled"]].copy()
df = df[~df["is_cancelled"]].copy()

print(f"Rows after removing cancellations: {len(df)}")

# ---------------------------------------------------------
# 3. Drop rows with missing CustomerID
# ---------------------------------------------------------
# These are guest/unidentified transactions — useless for segmentation/churn
df = df.dropna(subset=["CustomerID"])
df["CustomerID"] = df["CustomerID"].astype(int)

print(f"Rows after dropping missing CustomerID: {len(df)}")

# ---------------------------------------------------------
# 4. Remove non-product StockCodes (postage, manual entries, etc.)
# ---------------------------------------------------------
JUNK_CODES = ["POST", "D", "M", "BANK CHARGES", "PADS", "DOT", "CRUK", "AMAZONFEE", "GIFT"]
df = df[~df["StockCode"].astype(str).str.upper().isin(JUNK_CODES)]

print(f"Rows after removing junk stock codes: {len(df)}")

# ---------------------------------------------------------
# 5. Remove zero/negative price and zero/negative quantity rows
# ---------------------------------------------------------
df = df[(df["Price"] > 0) & (df["Quantity"] > 0)]

print(f"Rows after removing invalid price/quantity: {len(df)}")

# ---------------------------------------------------------
# 6. Parse dates, add computed sales column
# ---------------------------------------------------------
df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"], format="mixed", errors="coerce")
df = df.dropna(subset=["InvoiceDate"])
df["sales_amount"] = df["Quantity"] * df["Price"]

# ---------------------------------------------------------
# 7. Drop exact duplicate rows
# ---------------------------------------------------------
before = len(df)
df = df.drop_duplicates()
print(f"Dropped {before - len(df)} exact duplicate rows")

# ---------------------------------------------------------
# 8. Build normalized tables matching your 5-table schema
# ---------------------------------------------------------

# --- Customers ---
customers = (
    df[["CustomerID", "Country"]]
    .drop_duplicates(subset=["CustomerID"])
    .rename(columns={"CustomerID": "customer_id", "Country": "country"})
    .reset_index(drop=True)
)

# --- Products ---
products = (
    df[["StockCode", "Description"]]
    .drop_duplicates(subset=["StockCode"])
    .rename(columns={"StockCode": "product_id", "Description": "product_name"})
    .reset_index(drop=True)
)
# Drop rows with missing descriptions
products = products.dropna(subset=["product_name"])

# --- SalesTransactions ---
transactions = df[[
    "Invoice", "StockCode", "CustomerID", "Quantity", "Price", "InvoiceDate", "sales_amount"
]].rename(columns={
    "Invoice": "invoice_id",
    "StockCode": "product_id",
    "CustomerID": "customer_id",
    "Quantity": "quantity",
    "Price": "unit_price",
    "InvoiceDate": "invoice_date",
})

# ---------------------------------------------------------
# 9. Synthesize Inventory table (dataset has no stock data)
# ---------------------------------------------------------
np.random.seed(42)  # reproducible

# Total units sold per product, used to seed realistic starting stock
sold_per_product = transactions.groupby("product_id")["quantity"].sum()

inventory_rows = []
for pid in products["product_id"]:
    total_sold = sold_per_product.get(pid, 0)
    # Starting stock: somewhere above total historical sales, so it doesn't go negative
    starting_stock = int(total_sold * np.random.uniform(1.2, 2.5)) + np.random.randint(20, 100)
    reorder_threshold = int(starting_stock * np.random.uniform(0.1, 0.2))
    inventory_rows.append({
        "product_id": pid,
        "current_stock": starting_stock,
        "reorder_threshold": reorder_threshold,
    })

inventory = pd.DataFrame(inventory_rows)

# ---------------------------------------------------------
# 10. Save everything
# ---------------------------------------------------------
customers.to_csv(f"{OUT_DIR}/customers.csv", index=False)
products.to_csv(f"{OUT_DIR}/products.csv", index=False)
transactions.to_csv(f"{OUT_DIR}/sales_transactions.csv", index=False)
inventory.to_csv(f"{OUT_DIR}/inventory.csv", index=False)
cancellations.to_csv(f"{OUT_DIR}/cancellations_raw.csv", index=False)

print("\nDone. Output files in ./cleaned_data/:")
print(f"  customers.csv          — {len(customers)} rows")
print(f"  products.csv            — {len(products)} rows")
print(f"  sales_transactions.csv  — {len(transactions)} rows")
print(f"  inventory.csv           — {len(inventory)} rows")
print(f"  cancellations_raw.csv   — {len(cancellations)} rows (kept aside, not loaded into main schema)")
