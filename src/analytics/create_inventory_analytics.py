import pandas as pd
from pathlib import Path

print("=" * 70)
print("MARKETMIND AI — PHASE 3")
print("STEP 4: INVENTORY ANALYTICAL DATASET")
print("=" * 70)

# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

PROCESSED_DIR = BASE_DIR / "data" / "processed"
OUTPUT_DIR = BASE_DIR / "data" / "analytical"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

INPUT_FILE = (
    PROCESSED_DIR /
    "retail_store_inventory_clean.csv"
)

OUTPUT_FILE = (
    OUTPUT_DIR /
    "inventory_analytics.csv"
)

# ============================================================
# LOAD
# ============================================================

df = pd.read_csv(INPUT_FILE)

print()
print(f"Original rows    : {len(df):,}")
print(f"Original columns : {len(df.columns)}")

# ============================================================
# DATE
# ============================================================

df["Date"] = pd.to_datetime(
    df["Date"],
    errors="coerce"
)

# ============================================================
# INVENTORY FEATURES
# ============================================================

# Stock after today's sales
df["estimated_stock_after_sales"] = (
    df["Inventory Level"] - df["Units Sold"]
)

# Inventory coverage relative to demand
df["inventory_to_demand_ratio"] = (
    df["Inventory Level"]
    / df["Demand Forecast"].replace(0, pd.NA)
)

# Difference between forecast and actual sales
df["forecast_error"] = (
    df["Demand Forecast"] - df["Units Sold"]
)

# Absolute forecast error
df["absolute_forecast_error"] = (
    df["forecast_error"].abs()
)

# Stock shortage indicator
df["stockout_risk"] = (
    df["Inventory Level"] < df["Demand Forecast"]
).astype(int)

# High demand indicator
df["high_demand"] = (
    df["Units Sold"] > df["Units Sold"].median()
).astype(int)

# Discount flag
df["discount_applied"] = (
    df["Discount"] > 0
).astype(int)

# Price difference from competitor
df["price_difference_competitor"] = (
    df["Price"] - df["Competitor Pricing"]
)

# ============================================================
# REMOVE ORIGINAL FORECAST COLUMN IF IT IS DUPLICATED
# ============================================================

if "Demand Forecast Original" in df.columns:
    df = df.drop(
        columns=["Demand Forecast Original"]
    )

# ============================================================
# VALIDATION
# ============================================================

print()
print("ANALYTICAL FEATURES CREATED")
print("-" * 50)

new_features = [
    "estimated_stock_after_sales",
    "inventory_to_demand_ratio",
    "forecast_error",
    "absolute_forecast_error",
    "stockout_risk",
    "high_demand",
    "discount_applied",
    "price_difference_competitor"
]

for column in new_features:
    print(f"✓ {column}")

# ============================================================
# SAVE
# ============================================================

df.to_csv(
    OUTPUT_FILE,
    index=False
)

# ============================================================
# REPORT
# ============================================================

print()
print("INVENTORY ANALYTICAL DATASET CREATED")
print("-" * 50)

print(f"Rows    : {len(df):,}")
print(f"Columns : {len(df.columns)}")

print()
print("Missing values:")

missing = df.isnull().sum()
missing = missing[missing > 0]

if len(missing) == 0:
    print("✓ No missing values")
else:
    print(missing)

print()
print(f"Duplicate rows: {df.duplicated().sum():,}")

print()
print(f"Output: {OUTPUT_FILE}")

print()
print("=" * 70)
print("PHASE 3 — STEP 4 COMPLETE")
print("=" * 70)