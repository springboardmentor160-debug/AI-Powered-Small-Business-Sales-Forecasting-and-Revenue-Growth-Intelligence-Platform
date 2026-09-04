import pandas as pd
from pathlib import Path

# ============================================================
# OLIST ORDERS — DATA CLEANING
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

INPUT_FILE = BASE_DIR / "data" / "raw" / "olist_orders_dataset.csv"
OUTPUT_FILE = BASE_DIR / "data" / "processed" / "olist_orders_cleaned.csv"

print("=" * 60)
print("OLIST ORDERS — DATA CLEANING")
print("=" * 60)

df = pd.read_csv(INPUT_FILE)

print(f"Original rows    : {len(df)}")
print(f"Original columns : {len(df.columns)}")

# ------------------------------------------------------------
# 1. DUPLICATES
# ------------------------------------------------------------

duplicates = df.duplicated().sum()

print("\n[1] DUPLICATES")
print("-" * 50)
print(f"Duplicates found: {duplicates}")

df = df.drop_duplicates()

# ------------------------------------------------------------
# 2. DATE CONVERSION
# ------------------------------------------------------------

date_columns = [
    "order_purchase_timestamp",
    "order_approved_at",
    "order_delivered_carrier_date",
    "order_delivered_customer_date",
    "order_estimated_delivery_date"
]

print("\n[2] DATE CONVERSION")
print("-" * 50)

for col in date_columns:
    df[col] = pd.to_datetime(df[col], errors="coerce")

    print(
        f"{col:<35} "
        f"missing={df[col].isna().sum():<5}"
    )

# ------------------------------------------------------------
# 3. ORDER STATUS
# ------------------------------------------------------------

print("\n[3] ORDER STATUS")
print("-" * 50)

print(df["order_status"].value_counts())

# ------------------------------------------------------------
# 4. DATE LOGIC
# ------------------------------------------------------------

print("\n[4] DATE LOGIC")
print("-" * 50)

invalid_approval = (
    df["order_approved_at"].notna()
    & (
        df["order_approved_at"]
        < df["order_purchase_timestamp"]
    )
).sum()

invalid_carrier = (
    df["order_delivered_carrier_date"].notna()
    & df["order_approved_at"].notna()
    & (
        df["order_delivered_carrier_date"]
        < df["order_approved_at"]
    )
).sum()

invalid_delivery = (
    df["order_delivered_customer_date"].notna()
    & df["order_delivered_carrier_date"].notna()
    & (
        df["order_delivered_customer_date"]
        < df["order_delivered_carrier_date"]
    )
).sum()

print(f"Approval before purchase : {invalid_approval}")
print(f"Carrier before approval  : {invalid_carrier}")
print(f"Customer before carrier  : {invalid_delivery}")

# ------------------------------------------------------------
# 5. MISSING VALUES
# ------------------------------------------------------------

print("\n[5] MISSING VALUES")
print("-" * 50)

missing = df.isna().sum()

if missing.sum() == 0:
    print("✓ No missing values")
else:
    print(missing[missing > 0])

# IMPORTANT:
# We do NOT blindly fill missing delivery dates.
# Missing dates are legitimate for non-delivered orders.

# ------------------------------------------------------------
# 6. DELIVERY PERFORMANCE
# ------------------------------------------------------------

print("\n[6] DELIVERY PERFORMANCE")
print("-" * 50)

delivered = df[
    (df["order_status"] == "delivered")
    & df["order_delivered_customer_date"].notna()
    & df["order_estimated_delivery_date"].notna()
].copy()

delivered["delivery_difference_days"] = (
    delivered["order_delivered_customer_date"]
    - delivered["order_estimated_delivery_date"]
).dt.total_seconds() / 86400

late = (delivered["delivery_difference_days"] > 0).sum()
on_time = (delivered["delivery_difference_days"] <= 0).sum()

print(f"Delivered orders with valid dates : {len(delivered)}")
print(f"Late deliveries                    : {late}")
print(f"On-time/early deliveries            : {on_time}")

# ------------------------------------------------------------
# 7. FINAL DATASET
# ------------------------------------------------------------

OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

df.to_csv(OUTPUT_FILE, index=False)

print("\n[7] FINAL DATASET")
print("-" * 50)
print(f"Rows       : {len(df)}")
print(f"Columns    : {len(df.columns)}")
print(f"Saved to   : {OUTPUT_FILE}")

print("\n" + "=" * 60)
print("CLEANING COMPLETE")
print("=" * 60)