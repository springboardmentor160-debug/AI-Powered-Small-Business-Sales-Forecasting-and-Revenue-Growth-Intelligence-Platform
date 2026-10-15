"""M2 cleaning for the Online Retail II dataset (customer-level).
raw/online_retail_II.xlsx (both yearly sheets) or raw/OnlineRetail.csv -> processed/online_retail_prepped.csv"""
from pathlib import Path
import pandas as pd

BASE = Path(__file__).parent
RAW, OUT = BASE / "raw", BASE / "processed"
OUT.mkdir(exist_ok=True)
NON_PRODUCT = {"POST", "D", "M", "BANK CHARGES", "DOT", "CRUK", "AMAZONFEE", "ADJUST", "ADJUST2"}


def main():
    src = RAW / "OnlineRetail.csv"
    if src.exists():
        df = pd.read_csv(src, encoding="latin-1")
    else:
        df = pd.concat(pd.read_excel(RAW / "online_retail_II.xlsx", sheet_name=None).values(), ignore_index=True)
    df = df.rename(columns={"Invoice": "InvoiceNo", "Price": "UnitPrice", "Customer ID": "CustomerID"})
    n0 = len(df)
    print(f"Loaded {n0:,} rows | missing CustomerID: {df['CustomerID'].isna().sum():,} | duplicates: {df.duplicated().sum():,}")

    df["InvoiceNo"] = df["InvoiceNo"].astype(str).str.strip()
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"], errors="coerce")
    df = df.dropna(subset=["CustomerID", "InvoiceDate"])            # needed for segmentation / churn
    df = df[~df["InvoiceNo"].str.startswith("C")]                    # cancellations
    df = df[(df["Quantity"] > 0) & (df["UnitPrice"] > 0)]
    df["StockCode"] = df["StockCode"].astype(str).str.strip().str.upper()
    df = df[~df["StockCode"].isin(NON_PRODUCT)]
    df = df.drop_duplicates()
    df["CustomerID"] = df["CustomerID"].astype(float).astype(int).astype(str)
    df["Description"] = df["Description"].fillna("").astype(str).str.strip().str.upper()
    df["TotalAmount"] = (df["Quantity"] * df["UnitPrice"]).round(2)
    df = df[["InvoiceNo", "StockCode", "Description", "Quantity", "InvoiceDate", "UnitPrice", "CustomerID", "Country", "TotalAmount"]]
    df.to_csv(OUT / "online_retail_prepped.csv", index=False)
    print(f"Saved online_retail_prepped.csv: {len(df):,} rows ({n0-len(df):,} removed), {df['CustomerID'].nunique():,} customers, "
          f"{df['InvoiceDate'].min().date()} -> {df['InvoiceDate'].max().date()}")


if __name__ == "__main__":
    main()
