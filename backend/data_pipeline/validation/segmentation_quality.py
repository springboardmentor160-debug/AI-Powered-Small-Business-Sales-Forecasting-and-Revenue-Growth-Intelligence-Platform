from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[2]

SOURCE_FILES = [
    BASE_DIR / "online_retail_v1.csv",
    BASE_DIR / "online_retail_v2.csv",
]


def load_sources() -> pd.DataFrame:
    """Load source files without modifying them."""
    frames = [pd.read_csv(path) for path in SOURCE_FILES]
    return pd.concat(frames, ignore_index=True)


def main() -> None:
    print("=" * 65)
    print("MARKETMINDAI - SEGMENTATION DATA QUALITY CHECK")
    print("=" * 65)

    df = load_sources()

    df["Invoice"] = df["Invoice"].astype(str)
    df["Quantity"] = pd.to_numeric(df["Quantity"], errors="coerce")
    df["Price"] = pd.to_numeric(df["Price"], errors="coerce")

    total_amount = df["Quantity"] * df["Price"]

    cancellation_mask = df["Invoice"].str.startswith("C")
    negative_quantity_mask = df["Quantity"] < 0
    negative_amount_mask = total_amount < 0
    zero_quantity_mask = df["Quantity"] == 0
    zero_price_mask = df["Price"] == 0

    print(f"\nTotal source rows: {len(df):,}")

    print("\nPotential return/cancellation indicators:")
    print(
        f"Cancellation invoices : "
        f"{cancellation_mask.sum():,}"
    )
    print(
        f"Negative quantity      : "
        f"{negative_quantity_mask.sum():,}"
    )
    print(
        f"Negative amount        : "
        f"{negative_amount_mask.sum():,}"
    )
    print(
        f"Zero quantity          : "
        f"{zero_quantity_mask.sum():,}"
    )
    print(
        f"Zero price             : "
        f"{zero_price_mask.sum():,}"
    )

    print("\nPotential segmentation rows excluded by a sales-only rule:")

    segmentation_excluded = (
        cancellation_mask
        | negative_quantity_mask
        | negative_amount_mask
        | zero_quantity_mask
        | zero_price_mask
    )

    print(
        f"Rows flagged: "
        f"{segmentation_excluded.sum():,}"
    )

    print(
        f"Rows remaining: "
        f"{(~segmentation_excluded).sum():,}"
    )

    print("\nQuality check completed.")


if __name__ == "__main__":
    main()