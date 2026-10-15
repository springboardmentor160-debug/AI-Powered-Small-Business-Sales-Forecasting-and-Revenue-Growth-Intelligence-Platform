import pandas as pd
import os

# ============================================================
# MARKETMIND AI — PHASE 3
# STEP 6: ANALYTICAL DATASET ISSUE INSPECTION
# ============================================================

BASE_DIR = r"D:\project\MarketMind-AI"
ANALYTICAL_DIR = os.path.join(BASE_DIR, "data", "analytical")

SALES_FILE = os.path.join(ANALYTICAL_DIR, "sales_analytics.csv")
PRODUCT_FILE = os.path.join(ANALYTICAL_DIR, "product_analytics.csv")
INVENTORY_FILE = os.path.join(ANALYTICAL_DIR, "inventory_analytics.csv")


print("=" * 70)
print("MARKETMIND AI — PHASE 3")
print("STEP 6: ANALYTICAL DATASET ISSUE INSPECTION")
print("=" * 70)


# ============================================================
# 1. SALES DATASET — NEGATIVE VALUES
# ============================================================

print("\n[1] SALES — NEGATIVE NUMERIC VALUES")
print("-" * 50)

sales = pd.read_csv(SALES_FILE)

numeric_sales = sales.select_dtypes(include="number")

negative_sales = (numeric_sales < 0).sum()

negative_sales = negative_sales[negative_sales > 0]

if len(negative_sales) == 0:
    print("✓ No negative numeric values found")
else:
    for column, count in negative_sales.items():
        print(f"{column:<35} negative values = {count:,}")

    print("\nSample negative values:")
    
    for column in negative_sales.index:
        values = sales.loc[sales[column] < 0, column]
        print(f"\n{column}:")
        print(values.head(10).to_string(index=False))


# ============================================================
# 2. INVENTORY DATASET — NEGATIVE VALUES
# ============================================================

print("\n\n[2] INVENTORY — NEGATIVE NUMERIC VALUES")
print("-" * 50)

inventory = pd.read_csv(INVENTORY_FILE)

numeric_inventory = inventory.select_dtypes(include="number")

negative_inventory = (numeric_inventory < 0).sum()

negative_inventory = negative_inventory[negative_inventory > 0]

if len(negative_inventory) == 0:
    print("✓ No negative numeric values found")
else:
    for column, count in negative_inventory.items():
        print(f"{column:<35} negative values = {count:,}")

    print("\nSample negative values:")

    for column in negative_inventory.index:
        values = inventory.loc[inventory[column] < 0, column]
        print(f"\n{column}:")
        print(values.head(10).to_string(index=False))


# ============================================================
# 3. INVENTORY RATIO — MISSING VALUES
# ============================================================

print("\n\n[3] INVENTORY — MISSING INVENTORY/DEMAND RATIO")
print("-" * 50)

missing_ratio = inventory["inventory_to_demand_ratio"].isna().sum()

print(f"Missing ratio values : {missing_ratio:,}")

if missing_ratio > 0:

    print("\nChecking Demand Forecast for those rows:")

    missing_ratio_rows = inventory[
        inventory["inventory_to_demand_ratio"].isna()
    ]

    print(
        missing_ratio_rows[
            [
                "Inventory Level",
                "Units Sold",
                "Demand Forecast",
                "inventory_to_demand_ratio"
            ]
        ].head(20).to_string(index=False)
    )

    print("\nDemand Forecast values among missing-ratio rows:")

    print(
        missing_ratio_rows["Demand Forecast"]
        .value_counts(dropna=False)
        .head(20)
    )


# ============================================================
# 4. PRODUCT CATEGORY — MISSING VALUES
# ============================================================

print("\n\n[4] PRODUCT — MISSING ENGLISH CATEGORY")
print("-" * 50)

products = pd.read_csv(PRODUCT_FILE)

missing_category = products[
    products["product_category_name_english"].isna()
]

print(f"Missing category rows : {len(missing_category):,}")

if len(missing_category) > 0:

    print("\nSample affected products:")

    columns_to_show = [
        "product_id",
        "product_category_name",
        "product_category_name_english"
    ]

    print(
        missing_category[columns_to_show]
        .head(20)
        .to_string(index=False)
    )


# ============================================================
# 5. SALES — MISSING DELIVERY INFORMATION
# ============================================================

print("\n\n[5] SALES — MISSING DELIVERY INFORMATION")
print("-" * 50)

delivery_columns = [
    "delivery_days",
    "delivery_delay_days"
]

for column in delivery_columns:

    if column in sales.columns:

        missing = sales[column].isna().sum()

        print(f"{column:<30} missing = {missing:,}")

        if missing > 0:

            print(f"\nOrder status for missing {column}:")

            print(
                sales.loc[
                    sales[column].isna(),
                    "order_status"
                ].value_counts(dropna=False)
            )


# ============================================================
# 6. CHECK DELIVERY VALUES
# ============================================================

print("\n\n[6] SALES — DELIVERY VALUE DISTRIBUTION")
print("-" * 50)

for column in delivery_columns:

    if column in sales.columns:

        print(f"\n{column}:")

        print(
            sales[column]
            .describe()
            .to_string()
        )


# ============================================================
# 7. FINAL ISSUE SUMMARY
# ============================================================

print("\n\n" + "=" * 70)
print("ISSUE INSPECTION SUMMARY")
print("=" * 70)

print("\nSales negative-value columns:")
if len(negative_sales) > 0:
    for column, count in negative_sales.items():
        print(f"  ⚠ {column}: {count:,}")
else:
    print("  ✓ None")

print("\nInventory negative-value columns:")
if len(negative_inventory) > 0:
    for column, count in negative_inventory.items():
        print(f"  ⚠ {column}: {count:,}")
else:
    print("  ✓ None")

print(f"\nMissing inventory ratio: {missing_ratio:,}")
print(f"Missing product categories: {len(missing_category):,}")

print(
    f"Missing delivery_days: "
    f"{sales['delivery_days'].isna().sum():,}"
)

print(
    f"Missing delivery_delay_days: "
    f"{sales['delivery_delay_days'].isna().sum():,}"
)

print("\n" + "=" * 70)
print("PHASE 3 — STEP 6 INSPECTION COMPLETE")
print("=" * 70)

print("\nIMPORTANT:")
print("No data was modified by this script.")
print("We will decide the correct treatment after reviewing the output.")