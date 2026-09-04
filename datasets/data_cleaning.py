"""
Data Cleaning & Preparation — MarketMind AI
Milestone 1, Day 5-6

Cleans and validates the two raw datasets before they're loaded into
PostgreSQL by backend/load_data.py:

    retail_sales_dataset_final.csv  ->  retail_sales_data_prepped.csv
    sales_data_final.csv            ->  sales_data_prepped.csv

    cd datasets
    python data_cleaning.py
"""

import pandas as pd

# ---------------------------------------------------------------------------
# Load raw data
# ---------------------------------------------------------------------------
a = pd.read_csv("raw/retail_sales_dataset_final.csv")
b = pd.read_csv("raw/sales_data_final.csv")


# ---------------------------------------------------------------------------
# 1. RETAIL_SALES_DATA (a) — exploration & validation
# ---------------------------------------------------------------------------
print("=== RETAIL_SALES_DATA ===")
print(a.info())
print(a.head())
print(a.describe())

print("\nMissing values per column:\n", a.isnull().sum())

print("\nDuplicate rows:", a.duplicated().sum())

# Transaction ID should be a unique key — this should be 0
print("Duplicate Transaction IDs:", a.duplicated(subset=["Transaction ID"]).sum())

# Sanity check: implausible ages
implausible_age = a[(a["Age"] < 18) | (a["Age"] > 100)]
print(f"\nRows with implausible age (<18 or >100): {len(implausible_age)}")
print(implausible_age)

print("\nMin quantity:", a["Quantity"].min())
print("Gender values:", a["Gender"].unique())
print("Min price per unit:", a["Price per Unit"].min())

# Confirm Total Amount is internally consistent
consistent_totals = a[a["Total Amount"] == a["Quantity"] * a["Price per Unit"]]
print(f"\nRows where Total Amount == Quantity * Price per Unit: "
      f"{len(consistent_totals)} / {len(a)}")

print("\nDate range:", a["Date"].min(), "to", a["Date"].max())


# ---------------------------------------------------------------------------
# 2. SALES_DATA (b) — exploration & validation
# ---------------------------------------------------------------------------
print("\n=== SALES_DATA ===")
print(b.info())
print(b.head())
print(b.describe())

print("\nMissing values per column:\n", b.isnull().sum())

print("\nDuplicate rows:", b.duplicated().sum())

# Date + Store ID + Product ID should be a unique key — this should be 0
print("Duplicate Date/Store ID/Product ID combos:",
      b.duplicated(subset=["Date", "Store ID", "Product ID"]).sum())

print("\nMin inventory level:", b["Inventory Level"].min())
print("Min price:", b["Price"].min())
print("Discount range:", b["Discount"].min(), "-", b["Discount"].max())
print("Min competitor pricing:", b["Competitor Pricing"].min())

print("\nCategory values:", b["Category"].unique())
print("Region values:", b["Region"].unique())
print("Weather Condition values:", b["Weather Condition"].unique())
print("Seasonality values:", b["Seasonality"].unique())

print("\nDate range:", b["Date"].min(), "to", b["Date"].max())

# Binary flag checks
print("\nPromotion values:", b["Promotion"].unique())
print("Epidemic values:", b["Epidemic"].unique())
print("Rows with negative Units Ordered:", (b["Units Ordered"] < 0).sum())

# Spot check: does a Product ID map to a single, consistent Category?
print("\nCategories seen for Product ID P0001:",
      b[b["Product ID"] == "P0001"]["Category"].unique())


# ---------------------------------------------------------------------------
# 2.5. Build product_lookup.csv (Product ID -> Category)
# ---------------------------------------------------------------------------
# Data quality issue found above: Product ID does NOT map to a single fixed
# Category in this dataset — every one of the 20 product IDs shows up with
# 2-3 different categories across rows (a synthetic-data generation
# artifact, confirmed across all products, not a few stray typos).
#
# The Products table needs exactly one category per product_id (it's the
# primary key), so a choice has to be made. Decision: take the MOST
# FREQUENT category per Product ID (mode), not just the first one seen —
# more statistically defensible than an arbitrary row-order pick.
#
# Documented as a known limitation: "Product category was found to be
# inconsistent per Product ID in sales_data (likely a synthetic data
# generation artifact) — resolved by taking the most frequent category
# per product for the Products lookup table."
n_inconsistent = (b.groupby("Product ID")["Category"].nunique() > 1).sum()
n_products = b["Product ID"].nunique()
print(f"\nProduct IDs with inconsistent categories: {n_inconsistent} / {n_products}")

product_lookup = (
    b.groupby("Product ID")["Category"]
    .agg(lambda x: x.value_counts().idxmax())
    .reset_index()
)
product_lookup.columns = ["Product ID", "Category"]
print("\nproduct_lookup.csv preview:")
print(product_lookup)


# ---------------------------------------------------------------------------
# 3. Convert Date columns to proper datetime dtype
# ---------------------------------------------------------------------------
a["Date"] = pd.to_datetime(a["Date"])
b["Date"] = pd.to_datetime(b["Date"])

print("\n=== After datetime conversion ===")
print(a.info())
print(b.info())


# ---------------------------------------------------------------------------
# 4. Write cleaned/prepped CSVs
# ---------------------------------------------------------------------------
import os
os.makedirs("processed", exist_ok=True)

a.to_csv("processed/retail_sales_data_prepped.csv", index=False)
b.to_csv("processed/sales_data_prepped.csv", index=False)
product_lookup.to_csv("processed/product_lookup.csv", index=False)

print("\nDone — wrote processed/retail_sales_data_prepped.csv, "
      "processed/sales_data_prepped.csv, processed/product_lookup.csv")