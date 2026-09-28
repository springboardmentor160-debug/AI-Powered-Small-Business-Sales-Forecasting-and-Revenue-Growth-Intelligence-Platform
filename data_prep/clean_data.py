"""Clean the MarketMind AI raw datasets into separate processed CSV files."""

from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"

INVENTORY_REORDER_DEFAULT = 20


SALES_COLUMNS = [
    "transaction_id",
    "date",
    "product_id",
    "product_name",
    "category",
    "quantity",
    "unit_price",
    "total_amount",
    "store_id",
    "customer_id",
    "payment_method",
]
INVENTORY_COLUMNS = [
    "product_id",
    "product_name",
    "category",
    "stock_level",
    "reorder_threshold",
    "store_id",
]
CUSTOMER_COLUMNS = [
    "customer_id",
    "name",
    "email",
    "gender",
    "age",
    "city",
    "registration_date",
]


def print_missing_values(data: pd.DataFrame) -> None:
    """Report missing values without changing the supplied DataFrame."""
    missing = data.isna().sum()
    print(missing.to_string())


def print_dataset_start(dataset_name: str, data: pd.DataFrame) -> None:
    """Print the raw-data checks required before cleaning."""
    print(f"\n{dataset_name} BEFORE CLEANING")
    print("-" * 72)
    print(f"Rows: {len(data):,}")
    print("Missing values by column:")
    print_missing_values(data)
    print(f"Duplicate rows: {data.duplicated().sum():,}")


def clean_sales(sales: pd.DataFrame) -> pd.DataFrame:
    """Clean sales records while retaining the raw sales file unchanged."""
    print_dataset_start("SALES", sales)
    before_rows = len(sales)
    cleaned = sales.copy()

    # Quantity is required for sales analysis; remove missing values rather than imputing them.
    cleaned["quantity"] = pd.to_numeric(cleaned["quantity"], errors="coerce")
    missing_quantity = int(cleaned["quantity"].isna().sum())
    if missing_quantity:
        small_missing_limit = max(1, int(before_rows * 0.05))
        if missing_quantity <= small_missing_limit:
            print(f"Missing quantity values: {missing_quantity:,}; removing those rows.")
        else:
            print(
                f"Missing quantity values: {missing_quantity:,}; quantity is required, "
                "so those rows will be removed without imputation."
            )
        cleaned = cleaned.dropna(subset=["quantity"])

    duplicate_rows = int(cleaned.duplicated().sum())
    cleaned = cleaned.drop_duplicates()
    print(f"Duplicate rows removed: {duplicate_rows:,}")

    # Convert dates for consistent downstream time-series analysis.
    parsed_dates = pd.to_datetime(cleaned["date"], errors="coerce")
    invalid_dates = int(parsed_dates.isna().sum())
    cleaned["date"] = parsed_dates
    if invalid_dates:
        print(f"Invalid or missing dates removed: {invalid_dates:,}")
        cleaned = cleaned.dropna(subset=["date"])

    cleaned["unit_price"] = pd.to_numeric(cleaned["unit_price"], errors="coerce")
    cleaned["total_amount"] = pd.to_numeric(cleaned["total_amount"], errors="coerce")
    invalid_price = int(cleaned["unit_price"].isna().sum())
    if invalid_price:
        print(f"Missing or invalid unit prices removed: {invalid_price:,}")
        cleaned = cleaned.dropna(subset=["unit_price"])

    invalid_quantity_or_price = (cleaned["quantity"] <= 0) | (cleaned["unit_price"] <= 0)
    invalid_quantity_or_price_count = int(invalid_quantity_or_price.sum())
    cleaned = cleaned.loc[~invalid_quantity_or_price].copy()
    print(f"Rows with non-positive quantity or unit price removed: {invalid_quantity_or_price_count:,}")

    missing_customer = cleaned["customer_id"].isna() | cleaned["customer_id"].astype("string").str.strip().eq("")
    missing_customer_count = int(missing_customer.sum())
    cleaned = cleaned.loc[~missing_customer].copy()
    print(f"Rows with missing customer_id removed: {missing_customer_count:,}")

    expected_amount = cleaned["quantity"] * cleaned["unit_price"]
    amount_mismatch = cleaned["total_amount"].isna() | (
        (cleaned["total_amount"] - expected_amount).abs() > 0.01
    )
    print(f"total_amount mismatches against quantity * unit_price: {int(amount_mismatch.sum()):,}")

    cleaned["date"] = cleaned["date"].dt.strftime("%Y-%m-%d")
    cleaned["quantity"] = cleaned["quantity"].astype(int)
    cleaned = cleaned[SALES_COLUMNS]
    print(f"SALES AFTER CLEANING: {len(cleaned):,} rows (before: {before_rows:,})")
    return cleaned


def clean_inventory(inventory: pd.DataFrame) -> pd.DataFrame:
    """Clean inventory records while retaining the raw inventory file unchanged."""
    print_dataset_start("INVENTORY", inventory)
    before_rows = len(inventory)
    cleaned = inventory.copy()

    cleaned["stock_level"] = pd.to_numeric(cleaned["stock_level"], errors="coerce")
    cleaned["reorder_threshold"] = pd.to_numeric(cleaned["reorder_threshold"], errors="coerce")

    missing_reorder = int(cleaned["reorder_threshold"].isna().sum())
    if missing_reorder:
        # Twenty units is the documented baseline default for a missing threshold.
        cleaned["reorder_threshold"] = cleaned["reorder_threshold"].fillna(INVENTORY_REORDER_DEFAULT)
        print(
            f"Missing reorder_threshold values filled: {missing_reorder:,} "
            f"(default: {INVENTORY_REORDER_DEFAULT})."
        )

    negative_stock = cleaned["stock_level"] < 0
    negative_stock_count = int(negative_stock.sum())
    cleaned = cleaned.loc[~negative_stock].copy()
    print(f"Records with negative stock_level removed: {negative_stock_count:,}")

    duplicate_rows = int(cleaned.duplicated().sum())
    cleaned = cleaned.drop_duplicates()
    print(f"Duplicate rows removed: {duplicate_rows:,}")

    cleaned["stock_level"] = cleaned["stock_level"].astype("Int64")
    cleaned["reorder_threshold"] = cleaned["reorder_threshold"].astype("Int64")
    cleaned = cleaned[INVENTORY_COLUMNS]
    print(f"INVENTORY AFTER CLEANING: {len(cleaned):,} rows (before: {before_rows:,})")
    return cleaned


def clean_customers(customers: pd.DataFrame) -> pd.DataFrame:
    """Clean customer records while retaining the raw customer file unchanged."""
    print_dataset_start("CUSTOMERS", customers)
    before_rows = len(customers)
    cleaned = customers.copy()

    # Standardize email for reliable matching and deduplication.
    cleaned["email"] = cleaned["email"].astype("string").str.strip().str.lower()

    invalid_customer_id = (
        cleaned["customer_id"].isna()
        | cleaned["customer_id"].astype("string").str.strip().eq("")
    )
    invalid_customer_id_count = int(invalid_customer_id.sum())
    cleaned = cleaned.loc[~invalid_customer_id].copy()
    print(f"Missing or blank customer_id records removed: {invalid_customer_id_count:,}")
    print(f"Valid customer identifiers remaining: {cleaned['customer_id'].nunique():,}")

    duplicate_emails = int(cleaned.duplicated(subset=["email"], keep="first").sum())
    cleaned = cleaned.drop_duplicates(subset=["email"], keep="first")
    print(f"Duplicate customer records removed by email: {duplicate_emails:,}")

    cleaned = cleaned[CUSTOMER_COLUMNS]
    print(f"CUSTOMERS AFTER CLEANING: {len(cleaned):,} rows (before: {before_rows:,})")
    return cleaned


def main() -> None:
    """Load raw files, clean copies, and save only processed outputs."""
    # The raw paths are read-only inputs; all writes go to data/processed/.
    sales = pd.read_csv(RAW_DIR / "sales" / "sales.csv")
    inventory = pd.read_csv(RAW_DIR / "inventory" / "inventory.csv")
    customers = pd.read_csv(RAW_DIR / "customers" / "customers.csv")

    cleaned_sales = clean_sales(sales)
    cleaned_inventory = clean_inventory(inventory)
    cleaned_customers = clean_customers(customers)

    output_paths = {
        "sales": PROCESSED_DIR / "sales" / "cleaned_sales.csv",
        "inventory": PROCESSED_DIR / "inventory" / "cleaned_inventory.csv",
        "customers": PROCESSED_DIR / "customers" / "cleaned_customers.csv",
    }
    for output_path in output_paths.values():
        output_path.parent.mkdir(parents=True, exist_ok=True)

    cleaned_sales.to_csv(output_paths["sales"], index=False)
    cleaned_inventory.to_csv(output_paths["inventory"], index=False)
    cleaned_customers.to_csv(output_paths["customers"], index=False)

    print("\nCLEANING COMPLETE")
    print("-" * 72)
    for dataset_name, output_path in output_paths.items():
        print(f"{dataset_name.title()}: {output_path.relative_to(BASE_DIR)}")


if __name__ == "__main__":
    main()
