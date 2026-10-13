"""Shared data preparation for Milestone 3 (recommendations, churn, anomalies).

All three M3 models start from the same clean transaction table so their
results agree with each other and with the Milestone 2 segmentation.
"""

import logging
from pathlib import Path

import pandas as pd

from backend.data_pipeline.sources.uci.loader import read_uci_transactions
from backend.data_pipeline.transforms.transaction_reconciliation import (
    reconcile_invoice_reversals,
)

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[2]

M3_ARTIFACT_DIR = PROJECT_ROOT / "artifacts" / "milestone-3"
SEGMENTS_FILE = (
    PROJECT_ROOT
    / "artifacts"
    / "milestone-2"
    / "segmentation"
    / "customer_segments_final.csv"
)

# StockCodes that are fees/adjustments, not real products. They would
# pollute recommendations and look like "anomalies" for the wrong reason.
NON_PRODUCT_CODES = {
    "POST", "DOT", "M", "C2", "D", "S", "BANK CHARGES", "ADJUST",
    "AMAZONFEE", "PADS", "CRUK", "B", "TEST001", "TEST002",
}


def _is_non_product(stock_code: pd.Series) -> pd.Series:
    code = stock_code.astype(str).str.upper()
    return (
        code.isin(NON_PRODUCT_CODES)
        | code.str.startswith("GIFT_")
        | code.str.startswith("DCGS")
    )


def artifact_dir(name: str) -> Path:
    path = M3_ARTIFACT_DIR / name
    path.mkdir(parents=True, exist_ok=True)
    return path


def load_clean_sales() -> pd.DataFrame:
    """Return completed, valid sales lines from both UCI files.

    Steps:
      1. Read both raw files (unchanged on disk).
      2. Remove the Dec-2010 overlap: 1,088 invoices appear identically in
         both files, so rows from the second file are dropped for them.
      3. Reconcile fully-cancelled invoices (same logic as Milestone 2).
      4. Keep positive quantity/price lines for real products.
    """
    df = read_uci_transactions()
    df = df.rename(columns={"InvoiceNo": "Invoice", "UnitPrice": "Price"})
    df["Invoice"] = df["Invoice"].astype(str)

    first_file_invoices = set(
        df.loc[df["_source_file"] == "online_retail_v1.csv", "Invoice"]
    )
    overlap = (df["_source_file"] == "online_retail_v2.csv") & df[
        "Invoice"
    ].isin(first_file_invoices)
    logger.info("Dropping %s overlapping rows from file 2", int(overlap.sum()))
    df = df.loc[~overlap].copy()

    df = reconcile_invoice_reversals(df)

    valid = (
        (~df["is_reversal"])
        & (~df["Invoice"].str.upper().str.startswith("C"))
        & (df["Quantity"] > 0)
        & (df["Price"] > 0)
        & df["InvoiceDate"].notna()
        & (~_is_non_product(df["StockCode"]))
    )
    sales = df.loc[valid].copy()
    sales["StockCode"] = sales["StockCode"].astype(str)
    sales["Description"] = sales["Description"].fillna("").str.strip()
    sales["line_total"] = sales["Quantity"] * sales["Price"]

    logger.info(
        "Clean sales: %s lines, %s invoices", len(sales), sales["Invoice"].nunique()
    )
    return sales
