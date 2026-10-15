"""ETL: load the prepped CSVs from ../datasets/processed into the SQLite database.

  python load_data.py                      # everything (online-retail lines ~777k rows, about a minute)
  python load_data.py --skip-transactions  # only the store data + catalogue (a few seconds)

Only the data tables (sales_transactions, products, customers, transactions) are replaced; users and invoices are untouched.
"""
import argparse

import pandas as pd
from sqlalchemy import insert

import models
from config import PROCESSED_DIR
from database import Base, engine

CHUNK = 20_000


def load(df: pd.DataFrame, model, replace: bool = True) -> None:
    table = model.__table__
    df = df[[c.name for c in table.columns if c.name in df.columns]]
    df = df.astype(object).where(df.notna(), None)          # NaN -> NULL
    with engine.begin() as conn:                             # one transaction per table: all or nothing
        if replace:
            conn.execute(table.delete())
        for start in range(0, len(df), CHUNK):
            conn.execute(insert(table), df.iloc[start:start + CHUNK].to_dict(orient="records"))
    print(f"  {table.name}: {len(df):,} rows")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--skip-transactions", action="store_true")
    a = ap.parse_args()
    Base.metadata.create_all(bind=engine)

    sales = pd.read_csv(PROCESSED_DIR / "sales_data_prepped.csv", parse_dates=["date"])
    sales["date"] = sales["date"].dt.date                    # SQLAlchemy Date needs datetime.date
    load(sales, models.SalesTransaction)
    load(pd.read_csv(PROCESSED_DIR / "product_lookup.csv"), models.Product)

    if not a.skip_transactions:
        tx = pd.read_csv(PROCESSED_DIR / "online_retail_prepped.csv", parse_dates=["InvoiceDate"],
                         dtype={"CustomerID": str, "StockCode": str, "InvoiceNo": str})
        cust = tx.sort_values("InvoiceDate").groupby("CustomerID")["Country"].last().reset_index()
        load(cust.rename(columns={"CustomerID": "customer_id", "Country": "country"}), models.Customer)
        tx = tx.rename(columns={"InvoiceNo": "invoice_no", "StockCode": "stock_code", "Description": "description",
                                "Quantity": "quantity", "InvoiceDate": "invoice_date", "UnitPrice": "unit_price",
                                "CustomerID": "customer_id", "Country": "country", "TotalAmount": "total_amount"})
        load(tx, models.Transaction)
    print("Done.")


if __name__ == "__main__":
    main()
