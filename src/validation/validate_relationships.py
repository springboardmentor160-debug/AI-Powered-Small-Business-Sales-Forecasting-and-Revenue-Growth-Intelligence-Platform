import pandas as pd
from pathlib import Path


# ============================================================
# MARKETMIND AI
# PHASE 2 — STEP 2
# PRIMARY & FOREIGN KEY RELATIONSHIP VALIDATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"


print("=" * 70)
print("MARKETMIND AI — PHASE 2")
print("PRIMARY & FOREIGN KEY RELATIONSHIP VALIDATION")
print("=" * 70)


# ------------------------------------------------------------
# LOAD DATA
# ------------------------------------------------------------

print("\n[1] LOADING DATASETS")
print("-" * 50)

customers = pd.read_csv(
    PROCESSED_DIR / "customers_clean.csv"
)

orders = pd.read_csv(
    PROCESSED_DIR / "orders_cleaned.csv"
)

order_items = pd.read_csv(
    PROCESSED_DIR / "order_items_clean.csv"
)

order_payments = pd.read_csv(
    PROCESSED_DIR / "order_payments_clean.csv"
)

order_reviews = pd.read_csv(
    PROCESSED_DIR / "order_reviews_clean.csv"
)

products = pd.read_csv(
    PROCESSED_DIR / "products_cleaned.csv"
)

sellers = pd.read_csv(
    PROCESSED_DIR / "sellers_cleaned.csv"
)

geolocation = pd.read_csv(
    PROCESSED_DIR / "geolocation_clean.csv"
)

category_translation = pd.read_csv(
    PROCESSED_DIR /
    "product_category_name_translation_cleaned.csv"
)


print("✓ All Olist datasets loaded")


# ------------------------------------------------------------
# HELPER FUNCTION
# ------------------------------------------------------------

def check_relationship(
    child_df,
    child_column,
    parent_df,
    parent_column,
    relationship_name
):

    child_values = set(
        child_df[child_column].dropna().unique()
    )

    parent_values = set(
        parent_df[parent_column].dropna().unique()
    )

    orphan_values = child_values - parent_values

    child_count = len(child_values)
    orphan_count = len(orphan_values)

    orphan_rows = child_df[
        child_df[child_column].isin(orphan_values)
    ]

    print(f"\n{relationship_name}")
    print("-" * 50)

    print(f"Child unique values  : {child_count:,}")
    print(f"Parent unique values : {len(parent_values):,}")
    print(f"Orphan unique values : {orphan_count:,}")
    print(f"Orphan rows          : {len(orphan_rows):,}")

    if orphan_count == 0:
        print("Status              : ✓ PASS")
    else:
        print("Status              : ⚠ ORPHANS FOUND")

    return orphan_count


# ------------------------------------------------------------
# 1. PRIMARY KEY CHECK
# ------------------------------------------------------------

print("\n[2] PRIMARY KEY VALIDATION")
print("-" * 50)

primary_keys = {
    "customers.customer_id": (
        customers,
        "customer_id"
    ),

    "orders.order_id": (
        orders,
        "order_id"
    ),

    "products.product_id": (
        products,
        "product_id"
    ),

    "sellers.seller_id": (
        sellers,
        "seller_id"
    ),

    "reviews.review_id": (
        order_reviews,
        "review_id"
    ),
}


for name, (df, column) in primary_keys.items():

    null_count = df[column].isna().sum()
    duplicate_count = df[column].duplicated().sum()

    print(f"\n{name}")
    print(f"Null IDs       : {null_count:,}")
    print(f"Duplicate IDs  : {duplicate_count:,}")

    if null_count == 0 and duplicate_count == 0:
        print("Status         : ✓ PASS")
    else:
        print("Status         : ⚠ CHECK REQUIRED")


# ------------------------------------------------------------
# 2. ORDER RELATIONSHIPS
# ------------------------------------------------------------

print("\n[3] ORDER RELATIONSHIPS")
print("=" * 50)


check_relationship(
    orders,
    "customer_id",
    customers,
    "customer_id",
    "ORDERS → CUSTOMERS"
)


check_relationship(
    order_items,
    "order_id",
    orders,
    "order_id",
    "ORDER ITEMS → ORDERS"
)


check_relationship(
    order_payments,
    "order_id",
    orders,
    "order_id",
    "ORDER PAYMENTS → ORDERS"
)


check_relationship(
    order_reviews,
    "order_id",
    orders,
    "order_id",
    "ORDER REVIEWS → ORDERS"
)


# ------------------------------------------------------------
# 3. PRODUCT RELATIONSHIP
# ------------------------------------------------------------

print("\n[4] PRODUCT RELATIONSHIPS")
print("=" * 50)


check_relationship(
    order_items,
    "product_id",
    products,
    "product_id",
    "ORDER ITEMS → PRODUCTS"
)


# ------------------------------------------------------------
# 4. SELLER RELATIONSHIP
# ------------------------------------------------------------

print("\n[5] SELLER RELATIONSHIP")
print("=" * 50)


check_relationship(
    order_items,
    "seller_id",
    sellers,
    "seller_id",
    "ORDER ITEMS → SELLERS"
)


# ------------------------------------------------------------
# 5. CUSTOMER GEOLOCATION
# ------------------------------------------------------------

print("\n[6] CUSTOMER GEOLOCATION")
print("=" * 50)


check_relationship(
    customers,
    "customer_zip_code_prefix",
    geolocation,
    "geolocation_zip_code_prefix",
    "CUSTOMERS → GEOLOCATION"
)


# ------------------------------------------------------------
# 6. SELLER GEOLOCATION
# ------------------------------------------------------------

print("\n[7] SELLER GEOLOCATION")
print("=" * 50)


check_relationship(
    sellers,
    "seller_zip_code_prefix",
    geolocation,
    "geolocation_zip_code_prefix",
    "SELLERS → GEOLOCATION"
)


# ------------------------------------------------------------
# 7. CATEGORY TRANSLATION
# ------------------------------------------------------------

print("\n[8] PRODUCT CATEGORY TRANSLATION")
print("=" * 50)


check_relationship(
    products.dropna(
        subset=["product_category_name"]
    ),
    "product_category_name",
    category_translation,
    "product_category_name",
    "PRODUCTS → CATEGORY TRANSLATION"
)


# ------------------------------------------------------------
# 8. ORDER ITEM ID VALIDATION
# ------------------------------------------------------------

print("\n[9] ORDER ITEM ID CHECK")
print("-" * 50)

item_id_min = order_items["order_item_id"].min()
item_id_max = order_items["order_item_id"].max()

print(f"Minimum order_item_id : {item_id_min}")
print(f"Maximum order_item_id : {item_id_max}")


# ------------------------------------------------------------
# 9. RELATIONSHIP SUMMARY
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("RELATIONSHIP VALIDATION COMPLETE")
print("=" * 70)

print("""
The following relationships were checked:

1. Orders → Customers
2. Order Items → Orders
3. Order Payments → Orders
4. Order Reviews → Orders
5. Order Items → Products
6. Order Items → Sellers
7. Customers → Geolocation
8. Sellers → Geolocation
9. Products → Category Translation
""")

print("=" * 70)
print("PHASE 2 — STEP 2 COMPLETE")
print("=" * 70)