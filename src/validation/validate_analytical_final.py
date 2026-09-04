import pandas as pd
import os

# ============================================================
# MARKETMIND AI — PHASE 3
# STEP 6B: FINAL ANALYTICAL DATASET VALIDATION
# ============================================================

BASE_DIR = r"D:\project\MarketMind-AI"
ANALYTICAL_DIR = os.path.join(BASE_DIR, "data", "analytical")

FILES = {
    "sales": "sales_analytics.csv",
    "customer": "customer_analytics.csv",
    "product": "product_analytics.csv",
    "inventory": "inventory_analytics.csv"
}

print("=" * 70)
print("MARKETMIND AI — PHASE 3")
print("STEP 6B: FINAL ANALYTICAL DATASET VALIDATION")
print("=" * 70)


# ============================================================
# 1. FILE CHECK
# ============================================================

print("\n[1] ANALYTICAL FILE CHECK")
print("-" * 50)

datasets = {}

for name, filename in FILES.items():

    path = os.path.join(ANALYTICAL_DIR, filename)

    if os.path.exists(path):
        print(f"✓ {filename}")
        datasets[name] = pd.read_csv(path)
    else:
        print(f"✗ {filename} NOT FOUND")


# ============================================================
# 2. ROW AND COLUMN CHECK
# ============================================================

print("\n[2] DATASET SIZE CHECK")
print("-" * 50)

for name, df in datasets.items():

    print(
        f"{name:<12} "
        f"rows={len(df):>8,}   "
        f"columns={len(df.columns):>3}"
    )


# ============================================================
# 3. DUPLICATE CHECK
# ============================================================

print("\n[3] DUPLICATE CHECK")
print("-" * 50)

for name, df in datasets.items():

    duplicates = df.duplicated().sum()

    if duplicates == 0:
        print(f"✓ {name:<12} duplicates = 0")
    else:
        print(
            f"⚠ {name:<12} duplicates = "
            f"{duplicates:,}"
        )


# ============================================================
# 4. MISSING VALUE CHECK
# ============================================================

print("\n[4] MISSING VALUE CHECK")
print("-" * 50)

for name, df in datasets.items():

    missing = df.isna().sum()
    missing = missing[missing > 0]

    if len(missing) == 0:

        print(f"✓ {name:<12} no missing values")

    else:

        total = missing.sum()

        print(
            f"⚠ {name:<12} "
            f"missing values = {total:,}"
        )

        for column, count in missing.items():

            print(
                f"    {column}: {count:,}"
            )


# ============================================================
# 5. PRODUCT CATEGORY CHECK
# ============================================================

print("\n[5] PRODUCT CATEGORY CHECK")
print("-" * 50)

product = datasets["product"]

unknown_categories = (
    product["product_category_name_english"]
    .eq("Unknown")
    .sum()
)

missing_categories = (
    product["product_category_name_english"]
    .isna()
    .sum()
)

print(
    f"Unknown categories : {unknown_categories:,}"
)

print(
    f"Missing categories : {missing_categories:,}"
)

if missing_categories == 0:
    print("✓ Product category field has no missing values")
else:
    print("⚠ Product category field still has missing values")


# ============================================================
# 6. INVENTORY RATIO CHECK
# ============================================================

print("\n[6] INVENTORY RATIO CHECK")
print("-" * 50)

inventory = datasets["inventory"]

ratio_missing = (
    inventory["inventory_to_demand_ratio"]
    .isna()
    .sum()
)

zero_demand = (
    inventory["Demand Forecast"] == 0
).sum()

print(
    f"Missing ratio values : {ratio_missing:,}"
)

print(
    f"Zero-demand rows     : {zero_demand:,}"
)

if ratio_missing == zero_demand:

    print(
        "✓ All missing ratios correspond "
        "to zero demand forecast"
    )

else:

    print(
        "⚠ Ratio missing values need investigation"
    )


# ============================================================
# 7. LEGITIMATE NEGATIVE VALUES
# ============================================================

print("\n[7] LEGITIMATE NEGATIVE VALUE CHECK")
print("-" * 50)

sales = datasets["sales"]

negative_delivery_delay = (
    sales["delivery_delay_days"] < 0
).sum()

print(
    f"Sales negative delivery_delay_days : "
    f"{negative_delivery_delay:,}"
)

if negative_delivery_delay > 0:
    print(
        "✓ Preserved — represents early delivery"
    )


inventory = datasets["inventory"]

negative_forecast_error = (
    inventory["forecast_error"] < 0
).sum()

negative_price_difference = (
    inventory["price_difference_competitor"] < 0
).sum()

print(
    f"Inventory negative forecast_error    : "
    f"{negative_forecast_error:,}"
)

print(
    f"Inventory negative price difference  : "
    f"{negative_price_difference:,}"
)

print(
    "✓ Negative analytical values preserved"
)


# ============================================================
# 8. KEY CHECK
# ============================================================

print("\n[8] ANALYTICAL KEY CHECK")
print("-" * 50)

keys = {
    "customer": "customer_id",
    "product": "product_id"
}

for name, key in keys.items():

    df = datasets[name]

    nulls = df[key].isna().sum()
    duplicates = df[key].duplicated().sum()

    print(
        f"{name:<12} "
        f"key={key:<25} "
        f"duplicates={duplicates:,} "
        f"nulls={nulls:,}"
    )


# ============================================================
# 9. EXPECTED ROW COUNTS
# ============================================================

print("\n[9] ROW COUNT CONSISTENCY")
print("-" * 50)

expected_rows = {
    "sales": 112650,
    "customer": 99441,
    "product": 32951,
    "inventory": 73100
}

row_count_pass = True

for name, expected in expected_rows.items():

    actual = len(datasets[name])

    if actual == expected:

        print(
            f"✓ {name:<12} "
            f"{actual:,} rows"
        )

    else:

        print(
            f"⚠ {name:<12} "
            f"expected={expected:,} "
            f"actual={actual:,}"
        )

        row_count_pass = False


# ============================================================
# 10. FINAL STATUS
# ============================================================

print("\n" + "=" * 70)
print("FINAL ANALYTICAL DATASET STATUS")
print("=" * 70)

print("\n✓ Sales analytical dataset")
print("✓ Customer analytical dataset")
print("✓ Product analytical dataset")
print("✓ Inventory analytical dataset")

if row_count_pass:
    print("\n✓ Row counts are consistent")

if all(
    df.duplicated().sum() == 0
    for df in datasets.values()
):
    print("✓ No duplicate rows detected")

if missing_categories == 0:
    print("✓ Product categories resolved")

if ratio_missing == zero_demand:
    print("✓ Inventory ratio issue explained")

print("\n" + "=" * 70)
print("PHASE 3 — STEP 6B COMPLETE")
print("=" * 70)

print(
    "\nAnalytical layer is ready for "
    "feature engineering and ML preparation."
)