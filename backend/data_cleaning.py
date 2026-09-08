import pandas as pd

INPUT_FILE = "data/raw/sales_data.csv"
OUTPUT_FILE = "data/processed/clean_sales_data.csv"


def clean_data():
    print("Loading raw data...")

    df = pd.read_csv(INPUT_FILE)

    print(f"Original rows: {len(df)}")

    # Remove completely duplicated rows
    df = df.drop_duplicates()

    # Remove records with missing essential values
    df = df.dropna(subset=["quantity", "customer_id"])

    # Keep only valid quantities
    df = df[df["quantity"] > 0]

    # Keep only valid prices
    df = df[df["unit_price"] > 0]

    # Convert date to proper datetime format
    df["order_date"] = pd.to_datetime(
        df["order_date"],
        errors="coerce"
    )

    # Remove records with invalid dates
    df = df.dropna(subset=["order_date"])

    # Calculate total amount
    df["total_amount"] = (
        df["quantity"] * df["unit_price"]
    )

    # Save cleaned dataset
    df.to_csv(OUTPUT_FILE, index=False)

    print(f"Cleaned rows: {len(df)}")
    print(f"Removed rows: {14 - len(df)}")
    print(f"Saved cleaned data to: {OUTPUT_FILE}")


if __name__ == "__main__":
    clean_data()