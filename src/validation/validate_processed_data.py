import pandas as pd
from pathlib import Path


# ============================================================
# MARKETMIND AI
# PHASE 2 — STEP 1
# FINAL PROCESSED DATA VALIDATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"


# ------------------------------------------------------------
# Expected processed datasets
# ------------------------------------------------------------

DATASETS = {
    "customers": "customers_clean.csv",
    "geolocation": "geolocation_clean.csv",
    "order_items": "order_items_clean.csv",
    "order_payments": "order_payments_clean.csv",
    "order_reviews": "order_reviews_clean.csv",
    "orders": "orders_cleaned.csv",
    "category_translation": "product_category_name_translation_cleaned.csv",
    "products": "products_cleaned.csv",
    "retail_inventory": "retail_store_inventory_clean.csv",
    "sellers": "sellers_cleaned.csv",
}


print("=" * 70)
print("MARKETMIND AI — PHASE 2")
print("FINAL PROCESSED DATA VALIDATION")
print("=" * 70)


# ------------------------------------------------------------
# 1. CHECK PROCESSED DIRECTORY
# ------------------------------------------------------------

print("\n[1] PROCESSED DIRECTORY")
print("-" * 50)

if not PROCESSED_DIR.exists():
    print("ERROR: Processed directory does not exist:")
    print(PROCESSED_DIR)
    raise SystemExit

print("✓ Processed directory found")
print(f"Location: {PROCESSED_DIR}")


# ------------------------------------------------------------
# 2. CHECK FILES
# ------------------------------------------------------------

print("\n[2] DATASET FILE CHECK")
print("-" * 50)

missing_files = []

for name, filename in DATASETS.items():

    file_path = PROCESSED_DIR / filename

    if file_path.exists():
        print(f"✓ {filename}")
    else:
        print(f"✗ MISSING: {filename}")
        missing_files.append(filename)


# ------------------------------------------------------------
# STOP IF FILES ARE MISSING
# ------------------------------------------------------------

if missing_files:

    print("\n" + "=" * 70)
    print("VALIDATION STOPPED")
    print("=" * 70)

    print("\nMissing files:")

    for filename in missing_files:
        print(f"  - {filename}")

    print("\nCreate/fix the missing processed datasets before continuing.")

    raise SystemExit


# ------------------------------------------------------------
# 3. LOAD DATASETS
# ------------------------------------------------------------

print("\n[3] LOADING DATASETS")
print("-" * 50)

data = {}

for name, filename in DATASETS.items():

    file_path = PROCESSED_DIR / filename

    try:
        df = pd.read_csv(file_path)

        data[name] = df

        print(
            f"✓ {filename:<50} "
            f"Rows={len(df):>8,}  "
            f"Columns={len(df.columns):>3}"
        )

    except Exception as e:

        print(f"✗ ERROR loading {filename}")
        print(f"  {e}")

        raise SystemExit


# ------------------------------------------------------------
# 4. BASIC DATASET SUMMARY
# ------------------------------------------------------------

print("\n[4] DATASET SUMMARY")
print("-" * 50)

for name, df in data.items():

    print(
        f"{name:<20} "
        f"rows={len(df):>8,}   "
        f"columns={len(df.columns):>3}"
    )


# ------------------------------------------------------------
# 5. COLUMN LIST
# ------------------------------------------------------------

print("\n[5] COLUMN VALIDATION")
print("-" * 50)

for name, df in data.items():

    print(f"\n{name.upper()}")

    for column in df.columns:
        print(f"  - {column}")


# ------------------------------------------------------------
# 6. DUPLICATE ROW CHECK
# ------------------------------------------------------------

print("\n[6] DUPLICATE ROW CHECK")
print("-" * 50)

duplicate_problem = False

for name, df in data.items():

    duplicates = df.duplicated().sum()

    if duplicates == 0:
        print(f"✓ {name:<20} duplicates=0")
    else:
        print(
            f"⚠ {name:<20} duplicates={duplicates:,}"
        )
        duplicate_problem = True


# ------------------------------------------------------------
# 7. MISSING VALUE CHECK
# ------------------------------------------------------------

print("\n[7] MISSING VALUE CHECK")
print("-" * 50)

missing_problem = False

for name, df in data.items():

    total_missing = df.isna().sum().sum()

    if total_missing == 0:

        print(f"✓ {name:<20} missing=0")

    else:

        print(
            f"⚠ {name:<20} missing={total_missing:,}"
        )

        missing_problem = True

        missing_columns = df.isna().sum()

        missing_columns = missing_columns[
            missing_columns > 0
        ]

        for column, count in missing_columns.items():

            print(
                f"    {column}: {count:,}"
            )


# ------------------------------------------------------------
# 8. FINAL STATUS
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("FINAL VALIDATION SUMMARY")
print("=" * 70)

print(f"\nDatasets checked : {len(data)}")

if not duplicate_problem:
    print("Duplicate rows   : ✓ No duplicate rows detected")
else:
    print("Duplicate rows   : ⚠ Some duplicates detected")

if not missing_problem:
    print("Missing values   : ✓ No missing values detected")
else:
    print("Missing values   : ⚠ Missing values detected")


print("\n" + "=" * 70)
print("PHASE 2 — STEP 1 COMPLETE")
print("=" * 70)