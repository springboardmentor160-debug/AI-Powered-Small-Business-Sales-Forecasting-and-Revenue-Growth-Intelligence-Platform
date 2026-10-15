import pandas as pd
from pathlib import Path

# ============================================================
# MARKETMIND AI — PHASE 3
# STEP 1: SALES ANALYTICAL DATASET
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data" / "processed"
OUTPUT_DIR = BASE_DIR / "data" / "analytical"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

print("=" * 70)
print("MARKETMIND AI — PHASE 3")
print("STEP 1: SALES ANALYTICAL DATASET")
print("=" * 70)


# ============================================================
# LOAD DATA
# ============================================================

orders = pd.read_csv(
    DATA_DIR / "orders_cleaned.csv"
)

items = pd.read_csv(
    DATA_DIR / "order_items_clean.csv"
)

products = pd.read_csv(
    DATA_DIR / "products_cleaned.csv"
)

categories = pd.read_csv(
    DATA_DIR / "product_category_name_translation_cleaned.csv"
)


# ============================================================
# DATE CONVERSION
# ============================================================

orders["order_purchase_timestamp"] = pd.to_datetime(
    orders["order_purchase_timestamp"],
    errors="coerce"
)

orders["order_delivered_customer_date"] = pd.to_datetime(
    orders["order_delivered_customer_date"],
    errors="coerce"
)

orders["order_estimated_delivery_date"] = pd.to_datetime(
    orders["order_estimated_delivery_date"],
    errors="coerce"
)


# ============================================================
# MERGE ORDERS + ORDER ITEMS
# ============================================================

sales = orders.merge(
    items,
    on="order_id",
    how="inner"
)

print("\nAfter Orders + Order Items merge:")
print("Rows:", len(sales))


# ============================================================
# MERGE PRODUCTS
# ============================================================

sales = sales.merge(
    products[
        [
            "product_id",
            "product_category_name",
            "product_weight_g"
        ]
    ],
    on="product_id",
    how="left"
)

print("After Products merge:")
print("Rows:", len(sales))


# ============================================================
# MERGE CATEGORY TRANSLATION
# ============================================================

sales = sales.merge(
    categories,
    on="product_category_name",
    how="left"
)

print("After Category merge:")
print("Rows:", len(sales))


# ============================================================
# CREATE ANALYTICAL FEATURES
# ============================================================

sales["purchase_date"] = (
    sales["order_purchase_timestamp"]
    .dt.date
)

sales["purchase_year"] = (
    sales["order_purchase_timestamp"]
    .dt.year
)

sales["purchase_month"] = (
    sales["order_purchase_timestamp"]
    .dt.month
)

sales["purchase_day"] = (
    sales["order_purchase_timestamp"]
    .dt.day
)

sales["purchase_weekday"] = (
    sales["order_purchase_timestamp"]
    .dt.day_name()
)

sales["purchase_hour"] = (
    sales["order_purchase_timestamp"]
    .dt.hour
)


# ============================================================
# SALES VALUE
# ============================================================

sales["total_item_value"] = (
    sales["price"] +
    sales["freight_value"]
)


# ============================================================
# DELIVERY FEATURES
# ============================================================

sales["delivery_days"] = (
    sales["order_delivered_customer_date"]
    - sales["order_purchase_timestamp"]
).dt.total_seconds() / 86400

sales["estimated_delivery_days"] = (
    sales["order_estimated_delivery_date"]
    - sales["order_purchase_timestamp"]
).dt.total_seconds() / 86400

sales["delivery_delay_days"] = (
    sales["order_delivered_customer_date"]
    - sales["order_estimated_delivery_date"]
).dt.total_seconds() / 86400


# ============================================================
# LATE DELIVERY FLAG
# ============================================================

sales["is_late_delivery"] = (
    sales["delivery_delay_days"] > 0
).astype(int)


# ============================================================
# SELECT IMPORTANT COLUMNS
# ============================================================

final_columns = [
    "order_id",
    "customer_id",
    "product_id",
    "seller_id",
    "order_item_id",

    "order_status",
    "order_purchase_timestamp",

    "purchase_date",
    "purchase_year",
    "purchase_month",
    "purchase_day",
    "purchase_weekday",
    "purchase_hour",

    "product_category_name",
    "product_category_name_english",

    "price",
    "freight_value",
    "total_item_value",

    "product_weight_g",

    "delivery_days",
    "estimated_delivery_days",
    "delivery_delay_days",
    "is_late_delivery"
]

sales = sales[final_columns]


# ============================================================
# SAVE
# ============================================================

OUTPUT_FILE = OUTPUT_DIR / "sales_analytics.csv"

sales.to_csv(
    OUTPUT_FILE,
    index=False
)


# ============================================================
# VALIDATION
# ============================================================

print("\n" + "=" * 70)
print("SALES ANALYTICAL DATASET CREATED")
print("=" * 70)

print("Rows    :", len(sales))
print("Columns :", len(sales.columns))
print("Output  :", OUTPUT_FILE)

print("\nMissing values:")
print(
    sales.isna()
    .sum()
    .loc[lambda x: x > 0]
)

print("\nDuplicate rows:", sales.duplicated().sum())

print("\n" + "=" * 70)
print("PHASE 3 — STEP 1 COMPLETE")
print("=" * 70)