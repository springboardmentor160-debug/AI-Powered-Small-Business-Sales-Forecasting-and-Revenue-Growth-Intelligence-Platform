"""Initialize SQLite from the processed MarketMind datasets."""

import sqlite3
import os
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
DATABASE_PATH = Path(
    os.getenv("MARKETMIND_DATABASE_PATH", str(PROJECT_ROOT / "data" / "marketmind.db"))
)


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
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS invoices (
                invoice_id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_number TEXT NOT NULL UNIQUE,
                transaction_id TEXT NOT NULL UNIQUE,
                customer_id TEXT NOT NULL,
                store_id TEXT NOT NULL,
                transaction_date TEXT NOT NULL,
                issued_at TEXT NOT NULL,
                status TEXT NOT NULL CHECK (status = 'issued'),
                payment_status TEXT NOT NULL CHECK (payment_status = 'not_recorded'),
                paid_amount REAL NOT NULL DEFAULT 0 CHECK (paid_amount = 0),
                customer_name TEXT NOT NULL,
                customer_email TEXT,
                product_id TEXT NOT NULL,
                product_name TEXT NOT NULL,
                category TEXT,
                quantity INTEGER NOT NULL,
                unit_price REAL NOT NULL,
                total_amount REAL NOT NULL,
                payment_method TEXT,
                created_by_user_id INTEGER NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_invoices_customer_id "
            "ON invoices(customer_id)"
        )
        connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_invoices_store_id "
            "ON invoices(store_id)"
        )


def get_connection() -> sqlite3.Connection:
    """Return a row-producing connection to the initialized SQLite database."""
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection
