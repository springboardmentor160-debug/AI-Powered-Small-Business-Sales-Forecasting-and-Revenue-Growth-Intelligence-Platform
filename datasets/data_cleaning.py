"""M1 cleaning/validation for the operations (store/inventory/sales) dataset.
raw/retail_store_inventory.csv -> processed/sales_data_prepped.csv (+ product_lookup.csv)
Steps follow the Milestone 1 Day 5-6 guide: measure -> fix -> validate -> save separately."""
import re
from pathlib import Path
import numpy as np
import pandas as pd

BASE = Path(__file__).parent
RAW, OUT = BASE / "raw", BASE / "processed"
OUT.mkdir(exist_ok=True)


def snake(c):
    return re.sub(r"[^a-z0-9]+", "_", c.strip().lower()).strip("_")


def main():
    df = pd.read_csv(RAW / "retail_store_inventory.csv")
    df.columns = [snake(c) for c in df.columns]
    n0 = len(df)
    print(f"Loaded {n0:,} rows | missing cells: {int(df.isna().sum().sum())} | duplicates: {int(df.duplicated().sum())}")

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    for c in ["store_id", "product_id", "category", "region", "weather_condition", "seasonality"]:
        df[c] = df[c].astype(str).str.strip()
    df["category"] = df["category"].str.title()

    df = df.drop_duplicates()
    df = df.dropna(subset=["date", "store_id", "product_id", "units_sold", "price"])
    # invalid values (guide step 5)
    df = df[(df["units_sold"] >= 0) & (df["price"] > 0) & (df["inventory_level"] >= 0)].copy()
    df["discount"] = df["discount"].clip(0, 100)

    df["net_price"] = (df["price"] * (1 - df["discount"] / 100)).round(2)
    df["revenue"] = (df["units_sold"] * df["net_price"]).round(2)

    # reorder_point is not in the raw data -> derive per store/product (1x avg daily units sold, min 10)
    rp = df.groupby(["store_id", "product_id"])["units_sold"].transform("mean")
    df["reorder_point"] = np.maximum(np.ceil(rp), 10).astype(int)

    df = df.sort_values(["date", "store_id", "product_id"]).reset_index(drop=True)
    df.to_csv(OUT / "sales_data_prepped.csv", index=False)

    # product_id -> category lookup (raw data assigns a category per row; use the most frequent one)
    lookup = df.groupby("product_id").agg(
        category=("category", lambda s: s.mode().iat[0]), avg_price=("price", "mean")).round(2).reset_index()
    lookup.to_csv(OUT / "product_lookup.csv", index=False)
    print(f"Saved sales_data_prepped.csv: {len(df):,} rows ({n0-len(df):,} removed), "
          f"{df['date'].min().date()} -> {df['date'].max().date()}")
    print(f"Saved product_lookup.csv: {len(lookup)} products")


if __name__ == "__main__":
    main()
