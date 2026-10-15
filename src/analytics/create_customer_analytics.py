import pandas as pd
from pathlib import Path

print("=" * 70)
print("MARKETMIND AI — PHASE 3")
print("STEP 2: CUSTOMER ANALYTICAL DATASET")
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

customers = pd.read_csv(
    PROCESSED_DIR / "customers_clean.csv"
)

orders = pd.read_csv(
    PROCESSED_DIR / "orders_cleaned.csv"
)

order_items = pd.read_csv(
    PROCESSED_DIR / "order_items_clean.csv"
)

payments = pd.read_csv(
    PROCESSED_DIR / "order_payments_clean.csv"
)

reviews = pd.read_csv(
    PROCESSED_DIR / "order_reviews_clean.csv"
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

# ============================================================
# BASIC CUSTOMER INFORMATION
# ============================================================

customer_df = customers[
    [
        "customer_id",
        "customer_unique_id",
        "customer_zip_code_prefix",
        "customer_city",
        "customer_state"
    ]
].copy()

# ============================================================
# ORDER-LEVEL CUSTOMER FEATURES
# ============================================================

order_features = orders.groupby("customer_id").agg(
    total_orders=("order_id", "nunique"),
    first_purchase_date=("order_purchase_timestamp", "min"),
    last_purchase_date=("order_purchase_timestamp", "max"),
    delivered_orders=(
        "order_status",
        lambda x: (x == "delivered").sum()
    ),
    canceled_orders=(
        "order_status",
        lambda x: (x == "canceled").sum()
    )
).reset_index()

# ============================================================
# ORDER ITEM FEATURES
# ============================================================

item_features = order_items.groupby("order_id").agg(
    items_in_order=("order_item_id", "count"),
    total_item_value=("price", "sum"),
    total_freight_value=("freight_value", "sum")
).reset_index()

# Connect item information to customers
order_customer = orders[
    ["order_id", "customer_id"]
].merge(
    item_features,
    on="order_id",
    how="left"
)

customer_item_features = order_customer.groupby(
    "customer_id"
).agg(
    total_items=("items_in_order", "sum"),
    total_product_spend=("total_item_value", "sum"),
    total_freight_spend=("total_freight_value", "sum")
).reset_index()

# ============================================================
# PAYMENT FEATURES
# ============================================================

payment_features = payments.groupby("order_id").agg(
    order_payment_value=("payment_value", "sum")
).reset_index()

order_payment_customer = orders[
    ["order_id", "customer_id"]
].merge(
    payment_features,
    on="order_id",
    how="left"
)

customer_payment_features = order_payment_customer.groupby(
    "customer_id"
).agg(
    total_payment_value=("order_payment_value", "sum")
).reset_index()

# ============================================================
# REVIEW FEATURES
# ============================================================

review_features = reviews.groupby("order_id").agg(
    average_review_score=("review_score", "mean"),
    review_count=("review_id", "count")
).reset_index()

order_review_customer = orders[
    ["order_id", "customer_id"]
].merge(
    review_features,
    on="order_id",
    how="left"
)

customer_review_features = order_review_customer.groupby(
    "customer_id"
).agg(
    average_review_score=("average_review_score", "mean"),
    total_reviews=("review_count", "sum")
).reset_index()

# ============================================================
# MERGE CUSTOMER FEATURES
# ============================================================

customer_df = customer_df.merge(
    order_features,
    on="customer_id",
    how="left"
)

customer_df = customer_df.merge(
    customer_item_features,
    on="customer_id",
    how="left"
)

customer_df = customer_df.merge(
    customer_payment_features,
    on="customer_id",
    how="left"
)

customer_df = customer_df.merge(
    customer_review_features,
    on="customer_id",
    how="left"
)

# ============================================================
# DERIVED FEATURES
# ============================================================

customer_df["average_order_value"] = (
    customer_df["total_payment_value"]
    / customer_df["total_orders"]
)

customer_df["average_items_per_order"] = (
    customer_df["total_items"]
    / customer_df["total_orders"]
)

customer_df["delivery_rate"] = (
    customer_df["delivered_orders"]
    / customer_df["total_orders"]
)

customer_df["cancellation_rate"] = (
    customer_df["canceled_orders"]
    / customer_df["total_orders"]
)

# ============================================================
# FINAL CLEANUP
# ============================================================

numeric_columns = [
    "total_orders",
    "delivered_orders",
    "canceled_orders",
    "total_items",
    "total_product_spend",
    "total_freight_spend",
    "total_payment_value",
    "total_reviews",
    "average_order_value",
    "average_items_per_order",
    "delivery_rate",
    "cancellation_rate"
]

customer_df[numeric_columns] = customer_df[numeric_columns].fillna(0)

customer_df["average_review_score"] = (
    customer_df["average_review_score"].fillna(0)
)

# ============================================================
# SAVE
# ============================================================

OUTPUT_FILE = OUTPUT_DIR / "customer_analytics.csv"

customer_df.to_csv(
    OUTPUT_FILE,
    index=False
)

# ============================================================
# REPORT
# ============================================================

print()
print("CUSTOMER ANALYTICAL DATASET CREATED")
print("-" * 50)

print(f"Rows    : {len(customer_df):,}")
print(f"Columns : {len(customer_df.columns)}")

print()
print("Columns:")
for column in customer_df.columns:
    print(f"  - {column}")

print()
print("Missing values:")
missing = customer_df.isnull().sum()
missing = missing[missing > 0]

if len(missing) == 0:
    print("✓ No missing values")
else:
    print(missing)

print()
print(f"Duplicate rows: {customer_df.duplicated().sum():,}")

print()
print(f"Output: {OUTPUT_FILE}")

print()
print("=" * 70)
print("PHASE 3 — STEP 2 COMPLETE")
print("=" * 70)