import pandas as pd
from pathlib import Path

# ============================================================
# MARKETMIND AI — PHASE 2
# STEP 3: BUSINESS LOGIC VALIDATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "processed"

print("=" * 70)
print("MARKETMIND AI — PHASE 2")
print("STEP 3: BUSINESS LOGIC VALIDATION")
print("=" * 70)


# ============================================================
# LOAD DATASETS
# ============================================================

orders = pd.read_csv(DATA_DIR / "orders_cleaned.csv")
items = pd.read_csv(DATA_DIR / "order_items_clean.csv")
payments = pd.read_csv(DATA_DIR / "order_payments_clean.csv")
reviews = pd.read_csv(DATA_DIR / "order_reviews_clean.csv")
products = pd.read_csv(DATA_DIR / "products_cleaned.csv")
customers = pd.read_csv(DATA_DIR / "customers_clean.csv")
sellers = pd.read_csv(DATA_DIR / "sellers_cleaned.csv")
inventory = pd.read_csv(DATA_DIR / "retail_store_inventory_clean.csv")


# ============================================================
# 1. ORDER DATE LOGIC
# ============================================================

print("\n[1] ORDER DATE LOGIC")
print("-" * 50)

date_columns = [
    "order_purchase_timestamp",
    "order_approved_at",
    "order_delivered_carrier_date",
    "order_delivered_customer_date",
    "order_estimated_delivery_date"
]

for col in date_columns:
    orders[col] = pd.to_datetime(orders[col], errors="coerce")

purchase = orders["order_purchase_timestamp"]
approved = orders["order_approved_at"]
carrier = orders["order_delivered_carrier_date"]
customer_delivery = orders["order_delivered_customer_date"]
estimated = orders["order_estimated_delivery_date"]

approval_before_purchase = (
    approved.notna() &
    purchase.notna() &
    (approved < purchase)
).sum()

carrier_before_purchase = (
    carrier.notna() &
    purchase.notna() &
    (carrier < purchase)
).sum()

customer_before_purchase = (
    customer_delivery.notna() &
    purchase.notna() &
    (customer_delivery < purchase)
).sum()

customer_before_carrier = (
    customer_delivery.notna() &
    carrier.notna() &
    (customer_delivery < carrier)
).sum()

estimated_before_purchase = (
    estimated.notna() &
    purchase.notna() &
    (estimated < purchase)
).sum()

print(f"Approval before purchase      : {approval_before_purchase}")
print(f"Carrier before purchase       : {carrier_before_purchase}")
print(f"Customer delivery before buy : {customer_before_purchase}")
print(f"Customer before carrier       : {customer_before_carrier}")
print(f"Estimated delivery before buy : {estimated_before_purchase}")


# ============================================================
# 2. ORDER STATUS LOGIC
# ============================================================

print("\n[2] ORDER STATUS LOGIC")
print("-" * 50)

delivered = orders["order_status"] == "delivered"

delivered_missing_customer_date = (
    delivered & orders["order_delivered_customer_date"].isna()
).sum()

delivered_missing_carrier_date = (
    delivered & orders["order_delivered_carrier_date"].isna()
).sum()

non_delivered_with_customer_date = (
    (~delivered) &
    orders["order_delivered_customer_date"].notna()
).sum()

print(f"Delivered orders                  : {delivered.sum()}")
print(
    f"Delivered without customer date : "
    f"{delivered_missing_customer_date}"
)
print(
    f"Delivered without carrier date  : "
    f"{delivered_missing_carrier_date}"
)
print(
    f"Non-delivered with delivery date: "
    f"{non_delivered_with_customer_date}"
)


# ============================================================
# 3. ORDER ITEMS — PRICE & FREIGHT
# ============================================================

print("\n[3] ORDER ITEMS — PRICE & FREIGHT")
print("-" * 50)

negative_price = (items["price"] < 0).sum()
zero_price = (items["price"] == 0).sum()

negative_freight = (items["freight_value"] < 0).sum()
zero_freight = (items["freight_value"] == 0).sum()

print(f"Negative prices        : {negative_price}")
print(f"Zero prices            : {zero_price}")
print(f"Negative freight value : {negative_freight}")
print(f"Zero freight value     : {zero_freight}")

print(f"Price range            : "
      f"{items['price'].min():.2f} → {items['price'].max():.2f}")

print(f"Freight range          : "
      f"{items['freight_value'].min():.2f} → "
      f"{items['freight_value'].max():.2f}")


# ============================================================
# 4. PAYMENT VALIDATION
# ============================================================

print("\n[4] PAYMENT VALIDATION")
print("-" * 50)

negative_payment = (payments["payment_value"] < 0).sum()
zero_payment = (payments["payment_value"] == 0).sum()

invalid_installments = (
    payments["payment_installments"] <= 0
).sum()

print(f"Negative payment values : {negative_payment}")
print(f"Zero payment values     : {zero_payment}")
print(f"Invalid installments    : {invalid_installments}")

print(
    f"Payment value range     : "
    f"{payments['payment_value'].min():.2f} → "
    f"{payments['payment_value'].max():.2f}"
)


# ============================================================
# 5. REVIEW SCORE VALIDATION
# ============================================================

print("\n[5] REVIEW SCORE VALIDATION")
print("-" * 50)

invalid_review_scores = (
    (reviews["review_score"] < 1) |
    (reviews["review_score"] > 5)
).sum()

print(f"Invalid review scores : {invalid_review_scores}")
print(
    f"Review score range    : "
    f"{reviews['review_score'].min()} → "
    f"{reviews['review_score'].max()}"
)


# ============================================================
# 6. ORDER ITEM ID LOGIC
# ============================================================

print("\n[6] ORDER ITEM ID VALIDATION")
print("-" * 50)

invalid_item_ids = (
    items["order_item_id"] <= 0
).sum()

print(f"Invalid order_item_id values : {invalid_item_ids}")
print(
    f"Order item ID range          : "
    f"{items['order_item_id'].min()} → "
    f"{items['order_item_id'].max()}"
)


# ============================================================
# 7. PRODUCT DATA VALIDATION
# ============================================================

print("\n[7] PRODUCT DATA VALIDATION")
print("-" * 50)

negative_weight = (
    products["product_weight_g"] < 0
).sum()

negative_length = (
    products["product_length_cm"] < 0
).sum()

negative_height = (
    products["product_height_cm"] < 0
).sum()

negative_width = (
    products["product_width_cm"] < 0
).sum()

print(f"Negative product weight  : {negative_weight}")
print(f"Negative product length  : {negative_length}")
print(f"Negative product height  : {negative_height}")
print(f"Negative product width   : {negative_width}")


# ============================================================
# 8. CUSTOMER DATA VALIDATION
# ============================================================

print("\n[8] CUSTOMER DATA VALIDATION")
print("-" * 50)

null_customer_ids = customers["customer_id"].isna().sum()
null_unique_customer_ids = customers["customer_unique_id"].isna().sum()

duplicate_customer_ids = (
    customers["customer_id"].duplicated().sum()
)

print(f"Null customer_id             : {null_customer_ids}")
print(f"Null customer_unique_id      : {null_unique_customer_ids}")
print(f"Duplicate customer_id        : {duplicate_customer_ids}")


# ============================================================
# 9. SELLER DATA VALIDATION
# ============================================================

print("\n[9] SELLER DATA VALIDATION")
print("-" * 50)

null_seller_ids = sellers["seller_id"].isna().sum()
duplicate_seller_ids = sellers["seller_id"].duplicated().sum()

print(f"Null seller_id        : {null_seller_ids}")
print(f"Duplicate seller_id   : {duplicate_seller_ids}")


# ============================================================
# 10. RETAIL INVENTORY VALIDATION
# ============================================================

print("\n[10] RETAIL INVENTORY VALIDATION")
print("-" * 50)

inventory["Date"] = pd.to_datetime(
    inventory["Date"],
    errors="coerce"
)

print(
    f"Invalid dates          : "
    f"{inventory['Date'].isna().sum()}"
)

print(
    f"Negative inventory     : "
    f"{(inventory['Inventory Level'] < 0).sum()}"
)

print(
    f"Negative units sold    : "
    f"{(inventory['Units Sold'] < 0).sum()}"
)

print(
    f"Negative units ordered : "
    f"{(inventory['Units Ordered'] < 0).sum()}"
)

print(
    f"Negative price         : "
    f"{(inventory['Price'] < 0).sum()}"
)

print(
    f"Negative discount      : "
    f"{(inventory['Discount'] < 0).sum()}"
)

print(
    f"Invalid promotion flag : "
    f"{(~inventory['Holiday/Promotion'].isin([0, 1])).sum()}"
)


# ============================================================
# 11. BUSINESS LOGIC SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("BUSINESS LOGIC VALIDATION SUMMARY")
print("=" * 70)

checks = {
    "Approval before purchase": approval_before_purchase,
    "Carrier before purchase": carrier_before_purchase,
    "Customer before purchase": customer_before_purchase,
    "Customer before carrier": customer_before_carrier,
    "Estimated before purchase": estimated_before_purchase,
    "Delivered missing customer date": delivered_missing_customer_date,
    "Delivered missing carrier date": delivered_missing_carrier_date,
    "Negative item prices": negative_price,
    "Negative freight values": negative_freight,
    "Negative payment values": negative_payment,
    "Invalid payment installments": invalid_installments,
    "Invalid review scores": invalid_review_scores,
    "Invalid order item IDs": invalid_item_ids,
    "Negative product weights": negative_weight,
    "Negative product lengths": negative_length,
    "Negative product heights": negative_height,
    "Negative product widths": negative_width,
    "Invalid retail dates": inventory["Date"].isna().sum(),
    "Negative retail inventory": (
        inventory["Inventory Level"] < 0
    ).sum(),
    "Negative retail units sold": (
        inventory["Units Sold"] < 0
    ).sum(),
    "Negative retail units ordered": (
        inventory["Units Ordered"] < 0
    ).sum(),
}

issues = sum(value > 0 for value in checks.values())

for name, value in checks.items():
    status = "✓ PASS" if value == 0 else "⚠ CHECK"
    print(f"{status:<10} {name:<40}: {value}")

print("\nTotal checks with issues:", issues)

print("\n" + "=" * 70)
print("PHASE 2 — STEP 3 COMPLETE")
print("=" * 70)