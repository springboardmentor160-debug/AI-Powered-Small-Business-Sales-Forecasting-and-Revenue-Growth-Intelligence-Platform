"""
MarketMind AI — Kaggle Datasets Loader & Ingestion Module

Provides high-performance loaders for the project's Kaggle datasets using kagglehub:
1. 'umerkk12/online-retail-business' (or 'divanshu22/online-retail-dataset')
   - Real-world e-commerce sales transactions (>540k records).
   - Feeds sales analytics, forecasting, customer segmentation (RFM), churn risk, and market basket recommendations.
2. 'anirudhchauhan/retail-store-inventory-forecasting-dataset'
   - Multi-store retail inventory & demand forecasting dataset (73,100 records).
   - Feeds inventory control, stockout alerts, reorder thresholds, and demand intelligence.
"""

import os
import re
from pathlib import Path
from typing import Optional, Tuple
import pandas as pd
import kagglehub

# Default Dataset Identifiers
DATASET_ONLINE_RETAIL_CSV = "umerkk12/online-retail-business"
DATASET_ONLINE_RETAIL_XLSX = "divanshu22/online-retail-dataset"
DATASET_RETAIL_INVENTORY = "anirudhchauhan/retail-store-inventory-forecasting-dataset"

# Project paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"


def ensure_directories():
    """Ensure data directories exist."""
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)


def download_dataset(dataset_slug: str) -> str:
    """Download a dataset via kagglehub and return local directory path."""
    print(f"[KaggleHub] Downloading / checking dataset: {dataset_slug}...")
    download_path = kagglehub.dataset_download(dataset_slug)
    print(f"[KaggleHub] Dataset ready at: {download_path}")
    return download_path


def load_online_retail(
    sample_size: Optional[int] = None,
    as_sales_format: bool = True,
    prefer_csv: bool = True
) -> pd.DataFrame:
    """
    Downloads and loads the Online Retail dataset.
    
    Args:
        sample_size: If specified, caps the number of records returned.
        as_sales_format: If True, maps columns to MarketMind AI sales schema:
                         ['order_id', 'product_name', 'quantity', 'unit_price', 'order_date', 'customer_id', 'total_amount']
        prefer_csv: If True, uses umerkk12 (CSV, 44MB); otherwise divanshu22 (Excel, 22MB).
    """
    if prefer_csv:
        folder = download_dataset(DATASET_ONLINE_RETAIL_CSV)
        csv_file = Path(folder) / "OnlineRetail.csv"
        if not csv_file.exists():
            # Search in subdirectories
            matches = list(Path(folder).glob("**/*.csv"))
            if matches:
                csv_file = matches[0]
            else:
                raise FileNotFoundError(f"OnlineRetail.csv not found in {folder}")
        print(f"[DataLoader] Reading CSV: {csv_file}...")
        df = pd.read_csv(csv_file, encoding="latin1")
    else:
        folder = download_dataset(DATASET_ONLINE_RETAIL_XLSX)
        xlsx_file = Path(folder) / "customer.xlsx"
        if not xlsx_file.exists():
            matches = list(Path(folder).glob("**/*.xlsx"))
            if matches:
                xlsx_file = matches[0]
            else:
                raise FileNotFoundError(f"customer.xlsx not found in {folder}")
        print(f"[DataLoader] Reading Excel: {xlsx_file}...")
        df = pd.read_excel(xlsx_file)

    if not as_sales_format:
        if sample_size and len(df) > sample_size:
            return df.head(sample_size)
        return df

    print(f"[DataLoader] Cleaning and standardizing sales records (raw count: {len(df)})...")
    # Drop rows without CustomerID or Description
    df = df.dropna(subset=["CustomerID", "Description"])

    # Keep positive quantities and prices
    df = df[(df["Quantity"] > 0) & (df["UnitPrice"] > 0)].copy()

    # Parse dates safely
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"], format="mixed", errors="coerce")
    df = df.dropna(subset=["InvoiceDate"])
    df["order_date"] = df["InvoiceDate"].dt.strftime("%Y-%m-%d")

    # Clean description / product name
    df["product_name"] = df["Description"].astype(str).str.strip().str.title()

    # Format customer_id as C<ID>
    df["customer_id"] = "C" + df["CustomerID"].astype(int).astype(str)

    # Format order_id (extract digits from InvoiceNo, fallback to sequential)
    def clean_order_id(val, fallback_idx):
        digits = re.sub(r"\D", "", str(val))
        if digits:
            return int(digits[:9])
        return 1000000 + fallback_idx

    df["order_id"] = [clean_order_id(inv, idx) for idx, inv in enumerate(df["InvoiceNo"])]

    # Calculate total amount
    df["quantity"] = df["Quantity"].astype(int)
    df["unit_price"] = df["UnitPrice"].astype(float).round(2)
    df["total_amount"] = (df["quantity"] * df["unit_price"]).round(2)

    result_cols = [
        "order_id",
        "product_name",
        "quantity",
        "unit_price",
        "order_date",
        "customer_id",
        "total_amount"
    ]
    df_clean = df[result_cols].drop_duplicates()

    if sample_size and len(df_clean) > sample_size:
        df_clean = df_clean.head(sample_size)

    print(f"[DataLoader] Ready! Clean sales records: {len(df_clean)}")
    return df_clean


def load_retail_inventory(
    sample_size: Optional[int] = None,
    standardize_columns: bool = True
) -> pd.DataFrame:
    """
    Downloads and loads the Retail Store Inventory Forecasting dataset.
    
    Args:
        sample_size: Optional limit on rows returned.
        standardize_columns: If True, snake_cases the column names.
    """
    folder = download_dataset(DATASET_RETAIL_INVENTORY)
    csv_file = Path(folder) / "retail_store_inventory.csv"
    if not csv_file.exists():
        matches = list(Path(folder).glob("**/*.csv"))
        if matches:
            csv_file = matches[0]
        else:
            raise FileNotFoundError(f"retail_store_inventory.csv not found in {folder}")

    print(f"[DataLoader] Reading inventory CSV: {csv_file}...")
    df = pd.read_csv(csv_file)

    if standardize_columns:
        # Standardize column names to snake_case
        clean_cols = {
            "Date": "date",
            "Store ID": "store_id",
            "Product ID": "product_id",
            "Category": "category",
            "Region": "region",
            "Inventory Level": "stock_level",
            "Units Sold": "units_sold",
            "Units Ordered": "reorder_point",
            "Demand Forecast": "demand_forecast",
            "Price": "unit_price",
            "Discount": "discount",
            "Weather Condition": "weather_condition",
            "Holiday/Promotion": "is_holiday_promotion",
            "Competitor Pricing": "competitor_pricing",
            "Seasonality": "seasonality"
        }
        df = df.rename(columns=clean_cols)
        df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.strftime("%Y-%m-%d")

    if sample_size and len(df) > sample_size:
        df = df.head(sample_size)

    print(f"[DataLoader] Ready! Retail inventory records: {len(df)}")
    return df


def export_kaggle_datasets(
    sales_sample_size: Optional[int] = 10000,
    inventory_sample_size: Optional[int] = 10000
) -> Tuple[Path, Path]:
    """
    Downloads both datasets, cleans them, and exports them to project data folders:
    - data/processed/kaggle_clean_sales.csv
    - data/processed/kaggle_clean_inventory.csv
    """
    ensure_directories()

    sales_df = load_online_retail(sample_size=sales_sample_size, as_sales_format=True)
    sales_path = PROCESSED_DATA_DIR / "kaggle_clean_sales.csv"
    sales_df.to_csv(sales_path, index=False)
    print(f"[Export] Saved clean sales dataset ({len(sales_df)} rows) to: {sales_path}")

    inv_df = load_retail_inventory(sample_size=inventory_sample_size, standardize_columns=True)
    inv_path = PROCESSED_DATA_DIR / "kaggle_clean_inventory.csv"
    inv_df.to_csv(inv_path, index=False)
    print(f"[Export] Saved clean inventory dataset ({len(inv_df)} rows) to: {inv_path}")

    return sales_path, inv_path


if __name__ == "__main__":
    print("Testing Kaggle Data Ingestion Module...")
    export_kaggle_datasets(sales_sample_size=2000, inventory_sample_size=2000)
