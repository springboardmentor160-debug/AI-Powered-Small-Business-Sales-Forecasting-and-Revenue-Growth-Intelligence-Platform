import pandas as pd
from pathlib import Path

INPUT_FILE = Path("data/raw/olist_order_payments_dataset.csv")
OUTPUT_FILE = Path("data/processed/olist_order_payments_clean.csv")

OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(INPUT_FILE)

print("=" * 60)
print("OLIST ORDER PAYMENTS — DATA CLEANING")
print("=" * 60)

print(f"Original rows    : {len(df)}")
print(f"Original columns : {len(df.columns)}")


# ============================================================
# 1. DUPLICATES
# ============================================================

print("\n[1] DUPLICATES")
print("-" * 50)

duplicates = df.duplicated().sum()
print("Duplicate rows:", duplicates)

if duplicates > 0:
    df = df.drop_duplicates()


# ============================================================
# 2. MISSING VALUES
# ============================================================

print("\n[2] MISSING VALUES")
print("-" * 50)

missing = df.isna().sum()

if missing.sum() == 0:
    print("✓ No missing values")
else:
    print(missing[missing > 0])


# ============================================================
# 3. PAYMENT TYPES
# ============================================================

print("\n[3] PAYMENT TYPES")
print("-" * 50)

print(df["payment_type"].value_counts())


# ============================================================
# 4. PAYMENT VALUE CHECK
# ============================================================

print("\n[4] PAYMENT VALUE")
print("-" * 50)

print("Minimum:", df["payment_value"].min())
print("Maximum:", df["payment_value"].max())

print(
    "Negative payment values:",
    (df["payment_value"] < 0).sum()
)

print(
    "Zero payment values:",
    (df["payment_value"] == 0).sum()
)


# ============================================================
# 5. INSTALLMENTS
# ============================================================

print("\n[5] INSTALLMENTS")
print("-" * 50)

print("Minimum:", df["payment_installments"].min())
print("Maximum:", df["payment_installments"].max())

print(
    "Zero installments:",
    (df["payment_installments"] == 0).sum()
)


# ============================================================
# 6. PAYMENT SEQUENCE
# ============================================================

print("\n[6] PAYMENT SEQUENCE")
print("-" * 50)

print("Minimum:", df["payment_sequential"].min())
print("Maximum:", df["payment_sequential"].max())

print(
    "Invalid sequence <= 0:",
    (df["payment_sequential"] <= 0).sum()
)


# ============================================================
# 7. ORDER ID
# ============================================================

print("\n[7] ORDER ID")
print("-" * 50)

print("Missing order IDs:",
      df["order_id"].isna().sum())

print("Unique order IDs:",
      df["order_id"].nunique())


# ============================================================
# 8. FINAL CHECK
# ============================================================

print("\n[8] FINAL DATASET")
print("-" * 50)

print("Rows       :", len(df))
print("Columns    :", len(df.columns))
print("Duplicates :", df.duplicated().sum())


df.to_csv(OUTPUT_FILE, index=False)

print("\n" + "=" * 60)
print("CLEANING COMPLETE")
print("=" * 60)
print("Saved to:", OUTPUT_FILE)
