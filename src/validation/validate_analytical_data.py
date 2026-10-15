import pandas as pd
from pathlib import Path

print("=" * 70)
print("MARKETMIND AI — PHASE 3")
print("STEP 5: FINAL ANALYTICAL DATA VALIDATION")
print("=" * 70)

# ============================================================
# PATH
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

ANALYTICAL_DIR = (
    BASE_DIR /
    "data" /
    "analytical"
)

# ============================================================
# REQUIRED FILES
# ============================================================

FILES = {
    "sales": "sales_analytics.csv",
    "customer": "customer_analytics.csv",
    "product": "product_analytics.csv",
    "inventory": "inventory_analytics.csv"
}

# ============================================================
# FILE CHECK
# ============================================================

print()
print("[1] ANALYTICAL FILE CHECK")
print("-" * 50)

missing_files = []

for name, filename in FILES.items():

    path = ANALYTICAL_DIR / filename

    if path.exists():
        print(f"✓ {filename}")
    else:
        print(f"✗ {filename} — MISSING")
        missing_files.append(filename)

if missing_files:
    print()
    print("ERROR: Some analytical files are missing.")
    print("Create the missing datasets before continuing.")
    raise SystemExit(1)

# ============================================================
# LOAD DATASETS
# ============================================================

print()
print("[2] LOADING DATASETS")
print("-" * 50)

datasets = {}

for name, filename in FILES.items():

    path = ANALYTICAL_DIR / filename

    df = pd.read_csv(path)

    datasets[name] = df

    print(
        f"✓ {filename:<40}"
        f"Rows={len(df):>8,} "
        f"Columns={len(df.columns):>3}"
    )

# ============================================================
# DUPLICATE CHECK
# ============================================================

print()
print("[3] DUPLICATE CHECK")
print("-" * 50)

for name, df in datasets.items():

    duplicates = df.duplicated().sum()

    if duplicates == 0:
        print(f"✓ {name:<12} duplicates = 0")
    else:
        print(
            f"⚠ {name:<12} duplicates = "
            f"{duplicates:,}"
        )

# ============================================================
# MISSING VALUE CHECK
# ============================================================

print()
print("[4] MISSING VALUE CHECK")
print("-" * 50)

for name, df in datasets.items():

    total_missing = df.isnull().sum().sum()

    if total_missing == 0:

        print(
            f"✓ {name:<12} missing values = 0"
        )

    else:

        print(
            f"⚠ {name:<12} missing values = "
            f"{total_missing:,}"
        )

        missing_columns = (
            df.isnull()
            .sum()
        )

        missing_columns = (
            missing_columns[
                missing_columns > 0
            ]
        )

        for column, count in missing_columns.items():

            print(
                f"    {column}: "
                f"{count:,}"
            )

# ============================================================
# NEGATIVE VALUE CHECK
# ============================================================

print()
print("[5] NUMERIC NEGATIVE VALUE CHECK")
print("-" * 50)

for name, df in datasets.items():

    numeric_df = df.select_dtypes(
        include="number"
    )

    negative_count = (
        numeric_df < 0
    ).sum().sum()

    print(
        f"{name:<12} negative numeric values = "
        f"{negative_count:,}"
    )

# ============================================================
# DATE CHECK
# ============================================================

print()
print("[6] DATE COLUMN CHECK")
print("-" * 50)

if "Date" in datasets["inventory"].columns:

    dates = pd.to_datetime(
        datasets["inventory"]["Date"],
        errors="coerce"
    )

    invalid_dates = dates.isna().sum()

    print(
        f"Inventory invalid dates: "
        f"{invalid_dates}"
    )

# ============================================================
# KEY UNIQUENESS
# ============================================================

print()
print("[7] ANALYTICAL KEY CHECK")
print("-" * 50)

checks = {
    "customer": "customer_id",
    "product": "product_id",
    "inventory": None
}

for name, key in checks.items():

    if key is None:
        print(
            f"✓ {name:<12} "
            "transaction-level dataset"
        )
        continue

    df = datasets[name]

    if key in df.columns:

        duplicates = df[key].duplicated().sum()
        nulls = df[key].isna().sum()

        print(
            f"{name:<12} "
            f"key={key:<20} "
            f"duplicates={duplicates:,} "
            f"nulls={nulls:,}"
        )

# ============================================================
# FINAL SUMMARY
# ============================================================

print()
print("=" * 70)
print("FINAL ANALYTICAL DATASET SUMMARY")
print("=" * 70)

print()

for name, df in datasets.items():

    print(
        f"{name:<12} "
        f"Rows={len(df):>8,} "
        f"Columns={len(df.columns):>3}"
    )

print()
print("Analytical datasets:")
print("✓ Sales")
print("✓ Customer")
print("✓ Product")
print("✓ Inventory")

print()
print("=" * 70)
print("PHASE 3 — STEP 5 COMPLETE")
print("=" * 70)