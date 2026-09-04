import pandas as pd
from pathlib import Path

INPUT_FILE = Path("data/raw/olist_order_items_dataset.csv")
OUTPUT_FILE = Path("data/processed/olist_order_items_clean.csv")

OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(INPUT_FILE)

print("=" * 60)
print("OLIST ORDER ITEMS — DATA CLEANING")
print("=" * 60)

print(f"Original rows    : {len(df)}")
print(f"Original columns : {len(df.columns)}")


# ============================================================
# 1. DUPLICATES
# ============================================================

print("\n[1] DUPLICATES")
print("-" * 50)

duplicates = df.duplicated().sum()
print("Duplicate rows:", duplicates)

if duplicates > 0:
    df = df.drop_duplicates()


# ============================================================
# 2. MISSING VALUES
# ============================================================

print("\n[2] MISSING VALUES")
print("-" * 50)

missing = df.isna().sum()

if missing.sum() == 0:
    print("✓ No missing values")
else:
    print(missing[missing > 0])


# ============================================================
# 3. ORDER / PRODUCT / SELLER IDs
# ============================================================

print("\n[3] ID CHECK")
print("-" * 50)

for col in ["order_id", "product_id", "seller_id"]:
    print(
        f"{col:<20}"
        f"missing={df[col].isna().sum():<5}"
        f"unique={df[col].nunique()}"
    )


# ============================================================
# 4. SHIPPING DATE
# ============================================================

print("\n[4] SHIPPING DATE")
print("-" * 50)

df["shipping_limit_date"] = pd.to_datetime(
    df["shipping_limit_date"],
    errors="coerce"
)

print("Invalid dates:", df["shipping_limit_date"].isna().sum())

print(
    "Date range:",
    df["shipping_limit_date"].min(),
    "→",
    df["shipping_limit_date"].max()
)


# ============================================================
# 5. NUMERIC VALIDATION
# ============================================================

print("\n[5] NUMERIC VALIDATION")
print("-" * 50)

for col in ["order_item_id", "price", "freight_value"]:
    print(
        f"{col:<20}"
        f"min={df[col].min():.2f} "
        f"max={df[col].max():.2f}"
    )


# ============================================================
# 6. INVALID VALUES
# ============================================================

print("\n[6] INVALID VALUES")
print("-" * 50)

print("Price < 0:",
      (df["price"] < 0).sum())

print("Freight < 0:",
      (df["freight_value"] < 0).sum())

print("Order item ID <= 0:",
      (df["order_item_id"] <= 0).sum())


# ============================================================
# 7. FINAL CHECK
# ============================================================

print("\n[7] FINAL DATASET")
print("-" * 50)

print("Rows       :", len(df))
print("Columns    :", len(df.columns))
print("Duplicates :", df.duplicated().sum())


df.to_csv(OUTPUT_FILE, index=False)

print("\n" + "=" * 60)
print("CLEANING COMPLETE")
print("=" * 60)
print("Saved to:", OUTPUT_FILE)