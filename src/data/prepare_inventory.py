import pandas as pd
from pathlib import Path

# ============================================================
# PATHS
# ============================================================

INPUT_FILE = Path("data/raw/retail_store_inventory.csv")
OUTPUT_FILE = Path("data/processed/retail_store_inventory_clean.csv")

# Create processed folder if it doesn't exist
OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)


# ============================================================
# LOAD DATA
# ============================================================

df = pd.read_csv(INPUT_FILE)

print("=" * 60)
print("RETAIL STORE INVENTORY — DATA CLEANING")
print("=" * 60)

print(f"Original rows    : {len(df)}")
print(f"Original columns : {len(df.columns)}")


# ============================================================
# 1. CONVERT DATE
# ============================================================

df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

print("\n[1] DATE")
print("-" * 50)
print("Invalid dates:", df["Date"].isna().sum())
print("Date range   :", df["Date"].min(), "→", df["Date"].max())


# ============================================================
# 2. REMOVE EXACT DUPLICATES
# ============================================================

duplicates = df.duplicated().sum()

print("\n[2] DUPLICATES")
print("-" * 50)
print("Duplicates found:", duplicates)

if duplicates > 0:
    df = df.drop_duplicates()


# ============================================================
# 3. HANDLE NEGATIVE DEMAND FORECAST
# ============================================================

negative_count = (df["Demand Forecast"] < 0).sum()

print("\n[3] NEGATIVE DEMAND FORECAST")
print("-" * 50)
print("Negative values before cleaning:", negative_count)

# Keep original values for audit
df["Demand Forecast Original"] = df["Demand Forecast"]

# Demand cannot realistically be negative
df["Demand Forecast"] = df["Demand Forecast"].clip(lower=0)

print(
    "Negative values after cleaning:",
    (df["Demand Forecast"] < 0).sum()
)


# ============================================================
# 4. CHECK NUMERIC VALUES
# ============================================================

print("\n[4] NUMERIC VALIDATION")
print("-" * 50)

numeric_columns = [
    "Inventory Level",
    "Units Sold",
    "Units Ordered",
    "Demand Forecast",
    "Price",
    "Discount",
    "Holiday/Promotion",
    "Competitor Pricing"
]

for col in numeric_columns:
    print(
        f"{col:<25} "
        f"missing={df[col].isna().sum():<5} "
        f"min={df[col].min():.2f} "
        f"max={df[col].max():.2f}"
    )


# ============================================================
# 5. CHECK MISSING VALUES
# ============================================================

print("\n[5] MISSING VALUES")
print("-" * 50)

missing = df.isna().sum()

if missing.sum() == 0:
    print("✓ No missing values")
else:
    print(missing[missing > 0])


# ============================================================
# 6. CHECK CATEGORICAL VALUES
# ============================================================

print("\n[6] CATEGORICAL VALUES")
print("-" * 50)

categorical_columns = [
    "Store ID",
    "Product ID",
    "Category",
    "Region",
    "Weather Condition",
    "Seasonality"
]

for col in categorical_columns:
    print(f"\n{col}:")
    print(df[col].unique())


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