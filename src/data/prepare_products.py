import pandas as pd
from pathlib import Path

# ============================================================
# OLIST PRODUCTS — DATA CLEANING
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

INPUT_FILE = BASE_DIR / "data" / "raw" / "olist_products_dataset.csv"
OUTPUT_FILE = BASE_DIR / "data" / "processed" / "olist_products_cleaned.csv"

print("=" * 60)
print("OLIST PRODUCTS — DATA CLEANING")
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
# 2. MISSING VALUES
# ------------------------------------------------------------

print("\n[2] MISSING VALUES")
print("-" * 50)

print(df.isna().sum()[df.isna().sum() > 0])

# ------------------------------------------------------------
# 3. PRODUCT CATEGORY
# ------------------------------------------------------------

print("\n[3] PRODUCT CATEGORY")
print("-" * 50)

print(f"Unique categories: {df['product_category_name'].nunique()}")

# Keep missing categories as "unknown"
df["product_category_name"] = (
    df["product_category_name"]
    .fillna("unknown")
)

# ------------------------------------------------------------
# 4. NUMERIC COLUMNS
# ------------------------------------------------------------

numeric_columns = [
    "product_name_lenght",
    "product_description_lenght",
    "product_photos_qty",
    "product_weight_g",
    "product_length_cm",
    "product_height_cm",
    "product_width_cm"
]

print("\n[4] NUMERIC CLEANING")
print("-" * 50)

for col in numeric_columns:
    df[col] = pd.to_numeric(df[col], errors="coerce")

    # Missing values are filled with median
    if df[col].isna().sum() > 0:
        df[col] = df[col].fillna(df[col].median())

    print(
        f"{col:<35} "
        f"missing={df[col].isna().sum()}"
    )

# ------------------------------------------------------------
# 5. ZERO WEIGHT
# ------------------------------------------------------------

print("\n[5] ZERO WEIGHT")
print("-" * 50)

zero_weight = (df["product_weight_g"] <= 0).sum()

print(f"Invalid/zero weight rows: {zero_weight}")

# Replace zero weight with median positive weight
positive_weight = df.loc[
    df["product_weight_g"] > 0,
    "product_weight_g"
]

median_weight = positive_weight.median()

df.loc[
    df["product_weight_g"] <= 0,
    "product_weight_g"
] = median_weight

# ------------------------------------------------------------
# 6. FINAL CHECK
# ------------------------------------------------------------

print("\n[6] FINAL CHECK")
print("-" * 50)

print(f"Rows              : {len(df)}")
print(f"Columns           : {len(df.columns)}")
print(f"Duplicate rows    : {df.duplicated().sum()}")
print(f"Missing values    : {df.isna().sum().sum()}")
print(f"Unique product_id : {df['product_id'].nunique()}")

# ------------------------------------------------------------
# 7. SAVE
# ------------------------------------------------------------

OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

df.to_csv(OUTPUT_FILE, index=False)

print(f"\nSaved to: {OUTPUT_FILE}")

print("\n" + "=" * 60)
print("CLEANING COMPLETE")
print("=" * 60)