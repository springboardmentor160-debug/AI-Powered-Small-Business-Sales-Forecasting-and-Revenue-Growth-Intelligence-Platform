import pandas as pd
from pathlib import Path


# ============================================================
# PATHS
# ============================================================

INPUT_FILE = Path("data/raw/olist_geolocation_dataset.csv")
OUTPUT_FILE = Path("data/processed/olist_geolocation_clean.csv")

OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)


# ============================================================
# LOAD DATA
# ============================================================

df = pd.read_csv(INPUT_FILE)

print("=" * 60)
print("OLIST GEOLOCATION — DATA CLEANING")
print("=" * 60)

print(f"Original rows    : {len(df)}")
print(f"Original columns : {len(df.columns)}")


# ============================================================
# 1. DUPLICATE CHECK
# ============================================================

print("\n[1] DUPLICATES")
print("-" * 50)

duplicate_rows = df.duplicated().sum()

print("Duplicate rows:", duplicate_rows)

# Geolocation contains repeated observations for the same
# zip code/location, so remove only EXACT duplicate rows.
if duplicate_rows > 0:
    df = df.drop_duplicates()


# ============================================================
# 2. ZIP CODE CHECK
# ============================================================

print("\n[2] ZIP CODE CHECK")
print("-" * 50)

print(
    "Missing zip codes:",
    df["geolocation_zip_code_prefix"].isna().sum()
)

print(
    "Zip code range:",
    df["geolocation_zip_code_prefix"].min(),
    "→",
    df["geolocation_zip_code_prefix"].max()
)

print(
    "Unique zip codes:",
    df["geolocation_zip_code_prefix"].nunique()
)


# ============================================================
# 3. LATITUDE / LONGITUDE CHECK
# ============================================================

print("\n[3] COORDINATE CHECK")
print("-" * 50)

print(
    "Missing latitude:",
    df["geolocation_lat"].isna().sum()
)

print(
    "Missing longitude:",
    df["geolocation_lng"].isna().sum()
)

print(
    "Latitude range:",
    df["geolocation_lat"].min(),
    "→",
    df["geolocation_lat"].max()
)

print(
    "Longitude range:",
    df["geolocation_lng"].min(),
    "→",
    df["geolocation_lng"].max()
)


# ============================================================
# 4. LOCATION CHECK
# ============================================================

print("\n[4] LOCATION CHECK")
print("-" * 50)

for col in ["geolocation_city", "geolocation_state"]:
    print(
        f"{col:<25}"
        f"missing={df[col].isna().sum():<6}"
        f"unique={df[col].nunique()}"
    )


# ============================================================
# 5. MISSING VALUES
# ============================================================

print("\n[5] MISSING VALUES")
print("-" * 50)

missing = df.isna().sum()

if missing.sum() == 0:
    print("✓ No missing values")
else:
    print(missing[missing > 0])


# ============================================================
# 6. INVALID COORDINATES
# ============================================================

print("\n[6] INVALID COORDINATES")
print("-" * 50)

invalid_lat = (
    (df["geolocation_lat"] < -90) |
    (df["geolocation_lat"] > 90)
).sum()

invalid_lng = (
    (df["geolocation_lng"] < -180) |
    (df["geolocation_lng"] > 180)
).sum()

print("Invalid latitude :", invalid_lat)
print("Invalid longitude:", invalid_lng)


# ============================================================
# 7. STATE CHECK
# ============================================================

print("\n[7] STATE CHECK")
print("-" * 50)

print(
    "Unique states:",
    df["geolocation_state"].nunique()
)

print(
    sorted(df["geolocation_state"].unique())
)


# ============================================================
# 8. FINAL CHECK
# ============================================================

print("\n[8] FINAL DATASET")
print("-" * 50)

print("Rows       :", len(df))
print("Columns    :", len(df.columns))
print("Duplicates :", df.duplicated().sum())


# ============================================================
# SAVE CLEAN DATA
# ============================================================

df.to_csv(OUTPUT_FILE, index=False)

print("\n" + "=" * 60)
print("CLEANING COMPLETE")
print("=" * 60)

print("Saved to:")
print(OUTPUT_FILE)