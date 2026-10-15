"""M1: data-quality report on the PROCESSED datasets -> ml/outputs/data_quality.json (+ printed summary).
Measures what is actually in the files: rows, missing cells, duplicates, date coverage, value ranges, calendar gaps.
Run:  python datasets/data_quality_report.py"""
import json
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
PROC, OUT = ROOT / "datasets" / "processed", ROOT / "ml" / "outputs"
OUT.mkdir(parents=True, exist_ok=True)


def describe(df, date_col, numeric):
    full = pd.date_range(df[date_col].min().normalize(), df[date_col].max().normalize(), freq="D")
    return {"rows": int(len(df)), "columns": list(df.columns), "missing_cells": int(df.isna().sum().sum()),
            "missing_by_column": {c: int(n) for c, n in df.isna().sum().items() if n},
            "duplicate_rows": int(df.duplicated().sum()),
            "date_range": [str(df[date_col].min().date()), str(df[date_col].max().date())],
            "calendar_days_without_rows": int(len(full.difference(pd.DatetimeIndex(df[date_col].dt.normalize().unique())))),
            "numeric_ranges": {c: [float(df[c].min()), float(df[c].max())] for c in numeric}}


def main():
    sales = pd.read_csv(PROC / "sales_data_prepped.csv", parse_dates=["date"])
    online = pd.read_csv(PROC / "online_retail_prepped.csv", parse_dates=["InvoiceDate"], dtype={"CustomerID": str, "StockCode": str})
    rep = {
        "store_sales (retail_store_inventory)": {**describe(sales, "date", ["units_sold", "price", "inventory_level", "revenue", "reorder_point"]),
            "stores": int(sales["store_id"].nunique()), "products": int(sales["product_id"].nunique()),
            "invalid_rows": int(((sales["units_sold"] < 0) | (sales["price"] <= 0) | (sales["inventory_level"] < 0)).sum()),
            "provenance_note": "Public Kaggle-style store-inventory file. Its daily totals behave like random noise around a constant, "
                               "so it is most likely synthetic - do not present it as real-world retail data."},
        "online_retail_II": {**describe(online, "InvoiceDate", ["Quantity", "UnitPrice", "TotalAmount"]),
            "customers": int(online["CustomerID"].nunique()), "products": int(online["StockCode"].nunique()),
            "invalid_rows": int(((online["Quantity"] <= 0) | (online["UnitPrice"] <= 0)).sum()),
            "cancellation_invoices_left": int(online["InvoiceNo"].astype(str).str.startswith("C").sum()),
            "provenance_note": "UCI Online Retail II (real transactions of a UK online gift retailer, 2009-2011), cleaned by data_cleaning_segmentation.py."},
    }
    (OUT / "data_quality.json").write_text(json.dumps(rep, indent=2), encoding="utf-8")
    for k, v in rep.items():
        print(f"{k}: {v['rows']:,} rows | missing {v['missing_cells']} | duplicates {v['duplicate_rows']} | invalid {v['invalid_rows']} | "
              f"{v['date_range'][0]} -> {v['date_range'][1]} | days without rows {v['calendar_days_without_rows']}")


if __name__ == "__main__":
    main()
