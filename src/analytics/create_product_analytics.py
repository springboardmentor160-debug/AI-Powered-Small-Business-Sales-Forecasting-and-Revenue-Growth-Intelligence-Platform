import pandas as pd
from pathlib import Path

print("=" * 70)
print("MARKETMIND AI — PHASE 3")
print("STEP 3: PRODUCT ANALYTICAL DATASET")
print("=" * 70)

# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

PROCESSED_DIR = BASE_DIR / "data" / "processed"
OUTPUT_DIR = BASE_DIR / "data" / "analytical"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================
# LOAD DATA
# ============================================================

products = pd.read_csv(
    PROCESSED_DIR / "products_cleaned.csv"
)

order_items = pd.read_csv(
    PROCESSED_DIR / "order_items_clean.csv"
)

translation = pd.read_csv(
    PROCESSED_DIR /
    "product_category_name_translation_cleaned.csv"
)

# ============================================================
# PRODUCT BASE
# ============================================================

product_df = products.copy()

# ============================================================
# CATEGORY TRANSLATION
# ============================================================

product_df = product_df.merge(
    translation,
    on="product_category_name",
    how="left"
)

# ============================================================
# PRODUCT SALES FEATURES
# ============================================================

sales_features = order_items.groupby("product_id").agg(
    total_orders=("order_id", "nunique"),
    total_items_sold=("order_item_id", "count"),
    total_sales=("price", "sum"),
    total_freight=("freight_value", "sum"),
    average_price=("price", "mean"),
    average_freight=("freight_value", "mean"),
    minimum_price=("price", "min"),
    maximum_price=("price", "max"),
    unique_sellers=("seller_id", "nunique")
).reset_index()

# ============================================================
# MERGE
# ============================================================

product_df = product_df.merge(
    sales_features,
    on="product_id",
    how="left"
)

# ============================================================
# DERIVED FEATURES
# ============================================================

product_df["total_orders"] = (
    product_df["total_orders"].fillna(0)
)

product_df["total_items_sold"] = (
    product_df["total_items_sold"].fillna(0)
)

product_df["total_sales"] = (
    product_df["total_sales"].fillna(0)
)

product_df["total_freight"] = (
    product_df["total_freight"].fillna(0)
)

product_df["unique_sellers"] = (
    product_df["unique_sellers"].fillna(0)
)

product_df["average_price"] = (
    product_df["average_price"]
    .fillna(product_df["price"] if "price" in product_df.columns else 0)
)

product_df["sales_per_order"] = (
    product_df["total_sales"]
    / product_df["total_orders"].replace(0, pd.NA)
)

# ============================================================
# SAVE
# ============================================================

OUTPUT_FILE = OUTPUT_DIR / "product_analytics.csv"

product_df.to_csv(
    OUTPUT_FILE,
    index=False
)

# ============================================================
# REPORT
# ============================================================

print()
print("PRODUCT ANALYTICAL DATASET CREATED")
print("-" * 50)

print(f"Rows    : {len(product_df):,}")
print(f"Columns : {len(product_df.columns)}")

print()
print("Missing values:")

missing = product_df.isnull().sum()
missing = missing[missing > 0]

if len(missing) == 0:
    print("✓ No missing values")
else:
    print(missing)

print()
print(f"Duplicate rows: {product_df.duplicated().sum():,}")

print()
print(f"Output: {OUTPUT_FILE}")

print()
print("=" * 70)
print("PHASE 3 — STEP 3 COMPLETE")
print("=" * 70)