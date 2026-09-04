import pandas as pd
from pathlib import Path

INPUT_FILE = Path("data/raw/olist_order_reviews_dataset.csv")
OUTPUT_FILE = Path("data/processed/olist_order_reviews_clean.csv")

OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(INPUT_FILE)

print("=" * 60)
print("OLIST ORDER REVIEWS — DATA CLEANING")
print("=" * 60)

print(f"Original rows    : {len(df)}")
print(f"Original columns : {len(df.columns)}")


# ============================================================
# 1. EXACT DUPLICATES
# ============================================================

print("\n[1] EXACT DUPLICATES")
print("-" * 50)

duplicates = df.duplicated().sum()

print("Duplicate rows:", duplicates)

if duplicates > 0:
    df = df.drop_duplicates()


# ============================================================
# 2. REVIEW ID CHECK
# ============================================================

print("\n[2] REVIEW ID CHECK")
print("-" * 50)

print("Missing review IDs:",
      df["review_id"].isna().sum())

print("Unique review IDs:",
      df["review_id"].nunique())

print("Duplicate review IDs:",
      df["review_id"].duplicated().sum())


# ============================================================
# 3. ORDER ID CHECK
# ============================================================

print("\n[3] ORDER ID CHECK")
print("-" * 50)

print("Missing order IDs:",
      df["order_id"].isna().sum())

print("Unique orders:",
      df["order_id"].nunique())


# ============================================================
# 4. REVIEW SCORE
# ============================================================

print("\n[4] REVIEW SCORE")
print("-" * 50)

print(df["review_score"].value_counts().sort_index())

print(
    "Invalid scores:",
    (
        (df["review_score"] < 1) |
        (df["review_score"] > 5)
    ).sum()
)


# ============================================================
# 5. MISSING COMMENTS
# ============================================================

print("\n[5] COMMENTS")
print("-" * 50)

print(
    "Missing titles:",
    df["review_comment_title"].isna().sum()
)

print(
    "Missing messages:",
    df["review_comment_message"].isna().sum()
)


# ============================================================
# 6. DATE CONVERSION
# ============================================================

print("\n[6] DATES")
print("-" * 50)

date_columns = [
    "review_creation_date",
    "review_answer_timestamp"
]

for col in date_columns:

    df[col] = pd.to_datetime(
        df[col],
        errors="coerce"
    )

    print(
        f"{col:<25}"
        f"invalid={df[col].isna().sum()}"
    )


# ============================================================
# 7. DUPLICATE REVIEW IDs
# ============================================================

print("\n[7] DUPLICATE REVIEW IDs")
print("-" * 50)

duplicate_review_ids = df[
    df["review_id"].duplicated(keep=False)
]

print(
    "Rows involving duplicate review IDs:",
    len(duplicate_review_ids)
)

print(
    "Unique duplicate review IDs:",
    duplicate_review_ids["review_id"].nunique()
)


# IMPORTANT:
# We do NOT remove duplicate review IDs automatically.
#
# Our investigation showed that the same review_id can appear
# for multiple orders with identical score/comment information.
#
# We will handle this later during analytical dataset creation.


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