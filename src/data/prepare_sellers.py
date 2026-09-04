import pandas as pd
from pathlib import Path

# ============================================================
# OLIST SELLERS — DATA CLEANING
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

INPUT_FILE = BASE_DIR / "data" / "raw" / "olist_sellers_dataset.csv"
OUTPUT_FILE = BASE_DIR / "data" / "processed" / "olist_sellers_cleaned.csv"

print("=" * 60)
print("OLIST SELLERS — DATA CLEANING")
print("=" * 60)

df = pd.read_csv(INPUT_FILE)

print(f"Original rows    : {len(df)}")
print(f"Original columns : {len(df.columns)}")

# ------------------------------------------------------------
# 1. DUPLICATES
# ------------------------------------------------------------

print("\n[1] DUPLICATES")
print("-" * 50)

duplicates = df.duplicated().sum()

print(f"Duplicate rows: {duplicates}")

df = df.drop_duplicates()

# ------------------------------------------------------------
# 2. MISSING VALUES
# ------------------------------------------------------------

print("\n[2] MISSING VALUES")
print("-" * 50)

missing = df.isna().sum()

if missing.sum() == 0:
    print("✓ No missing values")
else:
    print(missing[missing > 0])

# ------------------------------------------------------------
# 3. SELLER ID CHECK
# ------------------------------------------------------------

print("\n[3] SELLER ID CHECK")
print("-" * 50)

print(f"Total sellers       : {len(df)}")
print(f"Unique seller_id    : {df['seller_id'].nunique()}")
print(f"Duplicate seller_id : {df['seller_id'].duplicated().sum()}")

# ------------------------------------------------------------
# 4. LOCATION CHECK
# ------------------------------------------------------------

print("\n[4] LOCATION CHECK")
print("-" * 50)

print(f"Unique cities : {df['seller_city'].nunique()}")
print(f"Unique states : {df['seller_state'].nunique()}")

# ------------------------------------------------------------
# 5. ZIP CODE CHECK
# ------------------------------------------------------------

print("\n[5] ZIP CODE CHECK")
print("-" * 50)

print(f"Minimum ZIP prefix : {df['seller_zip_code_prefix'].min()}")
print(f"Maximum ZIP prefix : {df['seller_zip_code_prefix'].max()}")

# ------------------------------------------------------------
# 6. FINAL CHECK
# ------------------------------------------------------------

print("\n[6] FINAL CHECK")
print("-" * 50)

print(f"Rows           : {len(df)}")
print(f"Columns        : {len(df.columns)}")
print(f"Duplicate rows : {df.duplicated().sum()}")
print(f"Missing values : {df.isna().sum().sum()}")

# ------------------------------------------------------------
# 7. SAVE
# ------------------------------------------------------------

OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

df.to_csv(OUTPUT_FILE, index=False)

print("\n[7] SAVED DATASET")
print("-" * 50)
print(f"Saved to: {OUTPUT_FILE}")

print("\n" + "=" * 60)
print("CLEANING COMPLETE")
print("=" * 60)