import pandas as pd
from pathlib import Path

# ============================================================
# PRODUCT CATEGORY NAME TRANSLATION — DATA CLEANING
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

INPUT_FILE = BASE_DIR / "data" / "raw" / "product_category_name_translation.csv"
OUTPUT_FILE = BASE_DIR / "data" / "processed" / "product_category_name_translation_cleaned.csv"

print("=" * 60)
print("PRODUCT CATEGORY NAME TRANSLATION — DATA CLEANING")
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
# 3. CATEGORY CHECK
# ------------------------------------------------------------

print("\n[3] CATEGORY CHECK")
print("-" * 50)

print(
    f"Unique Portuguese categories : "
    f"{df['product_category_name'].nunique()}"
)

print(
    f"Unique English categories    : "
    f"{df['product_category_name_english'].nunique()}"
)

# ------------------------------------------------------------
# 4. DUPLICATE CATEGORY NAMES
# ------------------------------------------------------------

print("\n[4] CATEGORY DUPLICATE CHECK")
print("-" * 50)

duplicate_portuguese = df[
    df["product_category_name"].duplicated(keep=False)
]

duplicate_english = df[
    df["product_category_name_english"].duplicated(keep=False)
]

print(
    f"Portuguese category duplicates : "
    f"{len(duplicate_portuguese)}"
)

print(
    f"English category duplicates    : "
    f"{len(duplicate_english)}"
)

# ------------------------------------------------------------
# 5. FINAL CHECK
# ------------------------------------------------------------

print("\n[5] FINAL CHECK")
print("-" * 50)

print(f"Rows           : {len(df)}")
print(f"Columns        : {len(df.columns)}")
print(f"Duplicate rows : {df.duplicated().sum()}")
print(f"Missing values : {df.isna().sum().sum()}")

# ------------------------------------------------------------
# 6. SAVE
# ------------------------------------------------------------

OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

df.to_csv(OUTPUT_FILE, index=False)

print("\n[6] SAVED DATASET")
print("-" * 50)
print(f"Saved to: {OUTPUT_FILE}")

print("\n" + "=" * 60)
print("CLEANING COMPLETE")
print("=" * 60)