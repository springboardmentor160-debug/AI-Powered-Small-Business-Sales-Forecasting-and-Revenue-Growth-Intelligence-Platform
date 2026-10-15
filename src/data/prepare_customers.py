import pandas as pd
from pathlib import Path


# ============================================================
# PATHS
# ============================================================

INPUT_FILE = Path("data/raw/olist_customers_dataset.csv")
OUTPUT_FILE = Path("data/processed/olist_customers_clean.csv")

OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)


# ============================================================
# LOAD DATA
# ============================================================

df = pd.read_csv(INPUT_FILE)

print("=" * 60)
print("OLIST CUSTOMERS — DATA CLEANING")
print("=" * 60)

print(f"Original rows    : {len(df)}")
print(f"Original columns : {len(df.columns)}")


# ============================================================
# 1. CHECK DUPLICATES
# ============================================================

print("\n[1] DUPLICATES")
print("-" * 50)

duplicate_rows = df.duplicated().sum()

print("Duplicate rows:", duplicate_rows)

if duplicate_rows > 0:
    df = df.drop_duplicates()


# ============================================================
# 2. CHECK CUSTOMER IDs
# ============================================================

print("\n[2] CUSTOMER ID CHECK")
print("-" * 50)

print("Missing customer_id:",
      df["customer_id"].isna().sum())

print("Duplicate customer_id:",
      df["customer_id"].duplicated().sum())

print("Missing customer_unique_id:",
      df["customer_unique_id"].isna().sum())

print("Unique customer_id:",
      df["customer_id"].nunique())

print("Unique customer_unique_id:",
      df["customer_unique_id"].nunique())


# ============================================================
# 3. CHECK ZIP CODE
# ============================================================

print("\n[3] ZIP CODE CHECK")
print("-" * 50)

print("Missing zip codes:",
      df["customer_zip_code_prefix"].isna().sum())

print(
    "Zip code range:",
    df["customer_zip_code_prefix"].min(),
    "→",
    df["customer_zip_code_prefix"].max()
)


# ============================================================
# 4. CHECK LOCATION DATA
# ============================================================

print("\n[4] LOCATION CHECK")
print("-" * 50)

location_columns = [
    "customer_city",
    "customer_state"
]

for col in location_columns:
    print(
        f"{col:<20} "
        f"missing={df[col].isna().sum():<5} "
        f"unique={df[col].nunique()}"
    )


# ============================================================
# 5. MISSING VALUES
# ============================================================

print("\n[5] MISSING VALUES")
print("-" * 50)

missing = df.isna().sum()

if missing.sum() == 0:
    print("✓ No missing values")
else:
    print(missing[missing > 0])


# ============================================================
# 6. CUSTOMER STATES
# ============================================================

print("\n[6] CUSTOMER STATES")
print("-" * 50)

print("Number of states:",
      df["customer_state"].nunique())

print("\nStates:")
print(sorted(df["customer_state"].unique()))


# ============================================================
# 7. FINAL CHECK
# ============================================================

print("\n[7] FINAL DATASET")
print("-" * 50)

print("Rows       :", len(df))
print("Columns    :", len(df.columns))
print("Duplicates :", df.duplicated().sum())


# ============================================================
# SAVE CLEAN DATA
# ============================================================

df.to_csv(OUTPUT_FILE, index=False)

print("\n" + "=" * 60)
print("CLEANING COMPLETE")
print("=" * 60)

print("Saved to:")
print(OUTPUT_FILE)