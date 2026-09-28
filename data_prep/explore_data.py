"""Explore the MarketMind AI raw datasets without modifying them."""

from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = BASE_DIR / "data" / "raw"

DATASET_PATHS = {
    "SALES": RAW_DIR / "sales" / "sales.csv",
    "INVENTORY": RAW_DIR / "inventory" / "inventory.csv",
    "CUSTOMERS": RAW_DIR / "customers" / "customers.csv",
}


def print_section(title: str) -> None:
    """Print a consistent heading so the terminal report is easy to scan."""
    print("\n" + "=" * 72)
    print(title)
    print("=" * 72)


def print_dataset_report(dataset_name: str, data: pd.DataFrame) -> None:
    """Print structural, quality, and summary statistics for one dataset."""
    print_section(f"{dataset_name} DATASET")
    print(f"Rows: {len(data):,}")
    print(f"Columns: {len(data.columns):,}")

    print("\nColumn names:")
    for column in data.columns:
        print(f"  - {column}")

    print("\nData types:")
    print(data.dtypes.to_string())

    print("\nMissing values by column:")
    print(data.isna().sum().to_string())

    print(f"\nDuplicate rows: {data.duplicated().sum():,}")

    print("\nBasic numerical statistics:")
    numerical_statistics = data.describe(include="number").transpose()
    if numerical_statistics.empty:
        print("No numerical columns.")
    else:
        print(numerical_statistics.to_string())

    if "customer_id" in data.columns:
        print(f"\nUnique customers: {data['customer_id'].nunique():,}")

    if "product_id" in data.columns:
        print(f"Unique products: {data['product_id'].nunique():,}")

    if dataset_name == "SALES":
        sales_dates = pd.to_datetime(data["date"])
        print(f"\nDate range: {sales_dates.min().date()} to {sales_dates.max().date()}")
        print(f"Total quantity sold: {data['quantity'].sum():,}")
        print(f"Total revenue: {data['total_amount'].sum():,.2f}")


def main() -> None:
    """Load each raw CSV and print exploration results only."""
    # Reading the files into DataFrames keeps this exploration read-only.
    datasets = {
        dataset_name: pd.read_csv(dataset_path)
        for dataset_name, dataset_path in DATASET_PATHS.items()
    }

    print_section("MARKETMIND AI RAW DATA EXPLORATION")
    print("This report reads the raw files only; no cleaning or transformation is performed.")

    for dataset_name, data in datasets.items():
        print_dataset_report(dataset_name, data)

    print_section("END OF REPORT")


if __name__ == "__main__":
    main()
