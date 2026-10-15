import pandas as pd

file = "data/raw/olist_products_dataset.csv"
df = pd.read_csv(file)

print("=" * 70)
print("OLIST PRODUCTS — FINAL DATA QUALITY CHECK")
print("=" * 70)

# ------------------------------------------------------------
# 1. BASIC INFO
# ------------------------------------------------------------

print("\n[1] BASIC INFO")
print("-" * 50)

print("Rows              :", len(df))
print("Columns           :", len(df.columns))
print("Duplicate rows    :", df.duplicated().sum())
print("Unique product_id :", df["product_id"].nunique())
print(
    "Duplicate product_id:",
    df["product_id"].duplicated().sum()
)

# ------------------------------------------------------------
# 2. MISSING VALUES
# ------------------------------------------------------------

print("\n[2] MISSING VALUES")
print("-" * 50)

missing = df.isna().sum()

print(
    missing[missing > 0].to_string()
    if (missing > 0).any()
    else "✓ No missing values"
)

# ------------------------------------------------------------
# 3. PRODUCT CATEGORY
# ------------------------------------------------------------

print("\n[3] PRODUCT CATEGORY")
print("-" * 50)

print(
    "Unique categories:",
    df["product_category_name"].nunique()
)

print("\nMissing category:", df["product_category_name"].isna().sum())

print("\nTop categories:")
print(
    df["product_category_name"]
    .value_counts()
    .head(15)
    .to_string()
)

# ------------------------------------------------------------
# 4. NUMERIC QUALITY
# ------------------------------------------------------------

numeric_cols = [
    "product_name_lenght",
    "product_description_lenght",
    "product_photos_qty",
    "product_weight_g",
    "product_length_cm",
    "product_height_cm",
    "product_width_cm"
]

print("\n[4] NUMERIC QUALITY")
print("-" * 50)

for col in numeric_cols:
    print(f"\n{col}")
    print("  Negative:", (df[col] < 0).sum())
    print("  Zero    :", (df[col] == 0).sum())
    print("  Min     :", df[col].min())
    print("  Max     :", df[col].max())

# ------------------------------------------------------------
# 5. MISSING CATEGORY + OTHER MISSING VALUES
# ------------------------------------------------------------

print("\n[5] ROWS WITH MISSING PRODUCT CATEGORY")
print("-" * 50)

missing_category = df[df["product_category_name"].isna()]

print("Rows:", len(missing_category))

if len(missing_category) > 0:
    print(
        missing_category.head(10).to_string(index=False)
    )

# ------------------------------------------------------------
# 6. PRODUCT ID FORMAT
# ------------------------------------------------------------

print("\n[6] PRODUCT ID CHECK")
print("-" * 50)

print("Null product IDs:", df["product_id"].isna().sum())
print("Unique product IDs:", df["product_id"].nunique())

# ------------------------------------------------------------
# 7. DIMENSION CONSISTENCY
# ------------------------------------------------------------

print("\n[7] DIMENSION CHECK")
print("-" * 50)

dimension_cols = [
    "product_weight_g",
    "product_length_cm",
    "product_height_cm",
    "product_width_cm"
]

for col in dimension_cols:
    print(
        f"{col:25} missing={df[col].isna().sum():4} "
        f"zero={(df[col] == 0).sum():4}"
    )

print("\n" + "=" * 70)
print("PRODUCTS CHECK COMPLETE")
print("=" * 70)