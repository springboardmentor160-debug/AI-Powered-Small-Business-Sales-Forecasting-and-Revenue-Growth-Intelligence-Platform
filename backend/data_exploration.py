import sys
import argparse
from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def profile_dataframe(df: pd.DataFrame, title: str):
    print(f"\n{'=' * 20} {title.upper()} {'=' * 20}")
    print(f"Rows: {len(df)} | Columns: {len(df.columns)}")
    print("\n[Columns & Types]")
    print(df.dtypes)
    print("\n[First 5 Rows]")
    print(df.head())
    print("\n[Summary Statistics]")
    print(df.describe(include="all"))
    print("\n[Missing Values]")
    print(df.isnull().sum())
    print("\n[Duplicate Rows]")
    print("Duplicate rows:", df.duplicated().sum())


def main():
    parser = argparse.ArgumentParser(description="Profile datasets for MarketMind AI")
    parser.add_argument(
        "--dataset",
        choices=["raw", "kaggle_sales", "kaggle_inventory", "all"],
        default="raw",
        help="Dataset to explore and profile"
    )
    args = parser.parse_args()

    raw_sales_path = PROJECT_ROOT / "data" / "raw" / "sales_data.csv"
    kaggle_sales_path = PROJECT_ROOT / "data" / "processed" / "kaggle_clean_sales.csv"
    kaggle_inv_path = PROJECT_ROOT / "data" / "processed" / "kaggle_clean_inventory.csv"

    if args.dataset in ["raw", "all"] and raw_sales_path.exists():
        df_raw = pd.read_csv(raw_sales_path)
        profile_dataframe(df_raw, "Raw Sales Dataset (data/raw/sales_data.csv)")

    if args.dataset in ["kaggle_sales", "all"] and kaggle_sales_path.exists():
        df_ksales = pd.read_csv(kaggle_sales_path)
        profile_dataframe(df_ksales, "Kaggle Clean Sales (Online Retail)")

    if args.dataset in ["kaggle_inventory", "all"] and kaggle_inv_path.exists():
        df_kinv = pd.read_csv(kaggle_inv_path)
        profile_dataframe(df_kinv, "Kaggle Clean Inventory (Store Inventory)")


if __name__ == "__main__":
    main()