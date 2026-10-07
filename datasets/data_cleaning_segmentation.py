"""
Data Cleaning & Preparation -- MarketMind AI
Milestone 2, Day 1-2 (Segmentation data source)

Cleans and validates the Online Retail dataset used for customer
segmentation (replaces retail_sales_dataset_final.csv, which had one
transaction per customer and could not support frequency-based features).

    OnlineRetail.csv  ->  online_retail_prepped.csv

Source: Kaggle "Online Retail Business" (umerkk12) / UCI Online Retail
dataset. 541,909 rows, 8 columns: InvoiceNo, StockCode, Description,
Quantity, InvoiceDate, UnitPrice, CustomerID, Country.

    cd datasets
    python data_cleaning_segmentation.py
"""

import pandas as pd

# ---------------------------------------------------------------------------
# Load raw data
# ---------------------------------------------------------------------------
df = pd.read_csv("raw/OnlineRetail.csv", encoding="latin1")

print("=== ONLINE RETAIL -- before cleaning ===")
print(df.info())
print(df.head())
print(df.describe())

# ---------------------------------------------------------------------------
# 1. Check the problems before fixing anything
# ---------------------------------------------------------------------------
print("\n=== Checks ===")
print("Missing values:\n", df.isnull().sum())
print("Duplicate rows:", df.duplicated().sum())
print("Quantity <= 0:", (df["Quantity"] <= 0).sum())
print("UnitPrice <= 0:", (df["UnitPrice"] <= 0).sum())
print("Cancellations (InvoiceNo starts with 'C'):",
      df["InvoiceNo"].astype(str).str.startswith("C").sum())
print("Unique CustomerID (before cleaning):", df["CustomerID"].nunique())

# ---------------------------------------------------------------------------
# 2. Drop rows with no CustomerID
# ---------------------------------------------------------------------------
# A row with no customer attached is unusable for customer-level
# segmentation -- there's no one to assign it to. ~25% of rows are
# affected, which is too many to drop blindly without noting it, but
# there's no alternative here: these rows cannot be reconstructed or
# meaningfully imputed.
before = len(df)
df = df.dropna(subset=["CustomerID"])
print(f"\nDropped {before - len(df)} rows with missing CustomerID")

# ---------------------------------------------------------------------------
# 3. Drop exact duplicate rows
# ---------------------------------------------------------------------------
before = len(df)
df = df.drop_duplicates()
print(f"Dropped {before - len(df)} exact duplicate rows")

# ---------------------------------------------------------------------------
# 4. Remove cancellations / returns
# ---------------------------------------------------------------------------
# InvoiceNo starting with 'C' marks a cancellation, which also shows up
# as a negative Quantity for the same line. These are real events in the
# business, but they are not purchases -- including them would distort
# purchase_frequency and purchase_value for segmentation. Excluded here,
# not silently dropped as "bad data".
before = len(df)
df = df[~df["InvoiceNo"].astype(str).str.startswith("C")]
print(f"Removed {before - len(df)} cancellation rows")

# ---------------------------------------------------------------------------
# 5. Remove non-sale rows (UnitPrice <= 0)
# ---------------------------------------------------------------------------
# Checked the Description values on these rows directly: "damages",
# "check", "adjustment", "thrown away", "sold as set on dotcom" -- these
# are internal stock-correction entries, not customer purchases. Safe to
# drop rather than flag.
before = len(df)
df = df[df["UnitPrice"] > 0]
print(f"Removed {before - len(df)} non-sale rows (UnitPrice <= 0)")

# ---------------------------------------------------------------------------
# 6. Quantity should be positive after cancellations are already removed
# ---------------------------------------------------------------------------
before = len(df)
df = df[df["Quantity"] > 0]
print(f"Removed {before - len(df)} remaining non-positive quantity rows")

# ---------------------------------------------------------------------------
# 7. Fix date formatting
# ---------------------------------------------------------------------------
df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"], format="%d-%m-%Y %H:%M")

# ---------------------------------------------------------------------------
# 8. Add a Total Amount column (not present in the raw file, but needed
#    downstream the same way it was used in M1's retail_sales dataset)
# ---------------------------------------------------------------------------
df["TotalAmount"] = df["Quantity"] * df["UnitPrice"]

# ---------------------------------------------------------------------------
# 9. CustomerID as a clean integer-like string, not a float (17850.0 -> "17850")
# ---------------------------------------------------------------------------
df["CustomerID"] = df["CustomerID"].astype(int).astype(str)

# ---------------------------------------------------------------------------
# Re-check after cleaning
# ---------------------------------------------------------------------------
print("\n=== ONLINE RETAIL -- after cleaning ===")
print(df.info())
print("Missing values:\n", df.isnull().sum())
print("Duplicate rows:", df.duplicated().sum())
print("Unique CustomerID (after cleaning):", df["CustomerID"].nunique())
print("Rows per customer -- min/mean/max:",
      df.groupby("CustomerID").size().min(),
      df.groupby("CustomerID").size().mean().round(1),
      df.groupby("CustomerID").size().max())
print("Date range:", df["InvoiceDate"].min(), "to", df["InvoiceDate"].max())

# ---------------------------------------------------------------------------
# Save cleaned data -- separate from raw, same convention as M1
# ---------------------------------------------------------------------------
df.to_csv("processed/online_retail_prepped.csv", index=False)
print(f"\nSaved {len(df)} cleaned rows to processed/online_retail_prepped.csv")