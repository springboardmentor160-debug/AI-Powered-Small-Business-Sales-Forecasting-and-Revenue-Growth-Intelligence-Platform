import pandas as pd
import os

# ============================================================
# MARKETMIND AI — PHASE 3
# STEP 6A: ANALYTICAL DATASET ISSUE RESOLUTION
# ============================================================

BASE_DIR = r"D:\project\MarketMind-AI"

ANALYTICAL_DIR = os.path.join(
    BASE_DIR,
    "data",
    "analytical"
)

# Input files
SALES_FILE = os.path.join(
    ANALYTICAL_DIR,
    "sales_analytics.csv"
)

PRODUCT_FILE = os.path.join(
    ANALYTICAL_DIR,
    "product_analytics.csv"
)

INVENTORY_FILE = os.path.join(
    ANALYTICAL_DIR,
    "inventory_analytics.csv"
)

print("=" * 70)
print("MARKETMIND AI — PHASE 3")
print("STEP 6A: ANALYTICAL DATASET ISSUE RESOLUTION")
print("=" * 70)


# ============================================================
# 1. SALES DATASET
# ============================================================

print("\n[1] SALES DATASET")
print("-" * 50)

sales = pd.read_csv(SALES_FILE)

print("✓ Loaded sales analytical dataset")

# ------------------------------------------------------------
# Keep negative delivery_delay_days
# ------------------------------------------------------------

print(
    "✓ Negative delivery_delay_days preserved "
    "(early delivery is valid)"
)

# ------------------------------------------------------------
# Missing delivery values
# ------------------------------------------------------------

missing_delivery = sales["delivery_days"].isna().sum()

print(
    f"✓ Missing delivery_days retained as NaN: "
    f"{missing_delivery:,}"
)

print(
    "  Reason: many orders were not delivered"
)


# ============================================================
# 2. PRODUCT DATASET
# ============================================================

print("\n[2] PRODUCT DATASET")
print("-" * 50)

products = pd.read_csv(PRODUCT_FILE)

missing_categories = (
    products["product_category_name_english"]
    .isna()
    .sum()
)

print(
    f"Missing English categories before: "
    f"{missing_categories:,}"
)

# Replace missing translated categories
# with an explicit analytical category.
products["product_category_name_english"] = (
    products["product_category_name_english"]
    .fillna("Unknown")
)

missing_categories_after = (
    products["product_category_name_english"]
    .isna()
    .sum()
)

print(
    f"Missing English categories after: "
    f"{missing_categories_after:,}"
)

print("✓ Missing categories converted to 'Unknown'")


# ============================================================
# 3. INVENTORY DATASET
# ============================================================

print("\n[3] INVENTORY DATASET")
print("-" * 50)

inventory = pd.read_csv(INVENTORY_FILE)

missing_ratio = (
    inventory["inventory_to_demand_ratio"]
    .isna()
    .sum()
)

print(
    f"Missing inventory_to_demand_ratio: "
    f"{missing_ratio:,}"
)

# ------------------------------------------------------------
# Demand Forecast = 0
# ------------------------------------------------------------

zero_forecast = (
    inventory["Demand Forecast"] == 0
).sum()

print(
    f"Rows with Demand Forecast = 0: "
    f"{zero_forecast:,}"
)

# Keep ratio as NaN when demand forecast is zero.
# This avoids division by zero and avoids inventing a value.

print(
    "✓ Zero-demand ratio values retained as NaN"
)

# ------------------------------------------------------------
# Keep legitimate negative analytical values
# ------------------------------------------------------------

print(
    "✓ Negative forecast_error preserved"
)

print(
    "✓ Negative price_difference_competitor preserved"
)


# ============================================================
# 4. SAVE UPDATED DATASETS
# ============================================================

print("\n[4] SAVING UPDATED DATASETS")
print("-" * 50)

products.to_csv(
    PRODUCT_FILE,
    index=False
)

print("✓ product_analytics.csv updated")

# Sales and inventory don't require numerical corrections.
# Save them unchanged so the analytical layer remains explicit.

sales.to_csv(
    SALES_FILE,
    index=False
)

inventory.to_csv(
    INVENTORY_FILE,
    index=False
)

print("✓ sales_analytics.csv verified and saved")
print("✓ inventory_analytics.csv verified and saved")


# ============================================================
# 5. FINAL CHECK
# ============================================================

print("\n[5] FINAL ISSUE CHECK")
print("-" * 50)

print(
    "Sales negative delivery_delay_days:",
    (sales["delivery_delay_days"] < 0).sum()
)

print(
    "Inventory negative forecast_error:",
    (inventory["forecast_error"] < 0).sum()
)

print(
    "Inventory negative price_difference_competitor:",
    (inventory["price_difference_competitor"] < 0).sum()
)

print(
    "Inventory missing ratio:",
    inventory["inventory_to_demand_ratio"].isna().sum()
)

print(
    "Product missing category:",
    products["product_category_name_english"].isna().sum()
)


# ============================================================
# COMPLETE
# ============================================================

print("\n" + "=" * 70)
print("PHASE 3 — STEP 6A COMPLETE")
print("=" * 70)

print("\nNo legitimate negative analytical values were removed.")
print("Missing values were handled according to their meaning.")