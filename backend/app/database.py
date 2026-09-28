"""Initialize SQLite from the processed MarketMind datasets."""

import sqlite3
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
DATABASE_PATH = PROJECT_ROOT / "data" / "marketmind.db"


DATASET_PATHS = {
    "sales_transactions": PROCESSED_DIR / "sales" / "cleaned_sales.csv",
    "inventory": PROCESSED_DIR / "inventory" / "cleaned_inventory.csv",
    "customers": PROCESSED_DIR / "customers" / "cleaned_customers.csv",
}


def initialize_database() -> None:
    """Load the current processed datasets into the local SQLite database."""
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

    missing_files = [path for path in DATASET_PATHS.values() if not path.exists()]
    if missing_files:
        missing = ", ".join(str(path) for path in missing_files)
        raise FileNotFoundError(f"Processed dataset(s) not found: {missing}")

    sales = pd.read_csv(DATASET_PATHS["sales_transactions"])
    inventory = pd.read_csv(DATASET_PATHS["inventory"])
    customers = pd.read_csv(DATASET_PATHS["customers"])
    products = inventory[["product_id", "product_name", "category"]].drop_duplicates("product_id")
    stores = inventory[["store_id"]].drop_duplicates()

    with sqlite3.connect(DATABASE_PATH) as connection:
        sales.to_sql("sales_transactions", connection, if_exists="replace", index=False)
        inventory.to_sql("inventory", connection, if_exists="replace", index=False)
        customers.to_sql("customers", connection, if_exists="replace", index=False)
        products.to_sql("products", connection, if_exists="replace", index=False)
        stores.to_sql("stores", connection, if_exists="replace", index=False)
        connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_sales_product_id "
            "ON sales_transactions(product_id)"
        )
        connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_sales_customer_id "
            "ON sales_transactions(customer_id)"
        )
        connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_inventory_product_id "
            "ON inventory(product_id)"
        )


def get_connection() -> sqlite3.Connection:
    """Return a row-producing connection to the initialized SQLite database."""
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection
