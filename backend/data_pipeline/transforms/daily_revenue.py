from pathlib import Path

import pandas as pd

from backend.data_pipeline.sources.uci.loader import (
    load_uci_online_retail,
)
from backend.data_pipeline.transforms.transaction_reconciliation import (
    reconcile_invoice_reversals,
)


OUTPUT_DIR = (
    Path(__file__).resolve().parents[3]
    / "artifacts"
    / "milestone-2"
    / "forecasting"
)


def build_completed_sales_transactions(
    sales_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Create the forecasting sales view from the UCI data.

    Rules:
        - valid customer ID
        - valid invoice date
        - non-cancellation invoice
        - positive quantity
        - positive price
        - positive transaction amount
        - exclude invoices identified as fully reversed

    The original source dataframe is never modified.
    """

    df = sales_df.copy()

    df["Invoice"] = df["Invoice"].astype(str)

    df["InvoiceDate"] = pd.to_datetime(
        df["InvoiceDate"],
        errors="coerce",
    )

    df["Quantity"] = pd.to_numeric(
        df["Quantity"],
        errors="coerce",
    )

    df["Price"] = pd.to_numeric(
        df["Price"],
        errors="coerce",
    )

    df["total_amount"] = (
        df["Quantity"] * df["Price"]
    )

    df = reconcile_invoice_reversals(df)

    eligible = (
        df["InvoiceDate"].notna()
        & (df["Quantity"] > 0)
        & (df["Price"] > 0)
        & (df["total_amount"] > 0)
        & ~df["Invoice"].str.upper().str.startswith("C")
        & ~df["is_reversal"]
    )

    completed_sales = df.loc[
        eligible
    ].copy()

    if completed_sales.empty:
        raise ValueError(
            "No completed sales transactions were "
            "available for forecasting."
        )

    return completed_sales


def build_daily_revenue(
    sales_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Aggregate completed sales into one row per day.

    Output columns:
        date
        revenue
    """

    completed_sales = (
        build_completed_sales_transactions(
            sales_df
        )
    )

    completed_sales["date"] = (
        completed_sales["InvoiceDate"]
        .dt.normalize()
    )

    daily_revenue = (
        completed_sales
        .groupby("date", as_index=False)["total_amount"]
        .sum()
        .rename(
            columns={
                "total_amount": "revenue",
            }
        )
        .sort_values("date")
        .reset_index(drop=True)
    )

    return daily_revenue


def validate_date_gaps(
    daily_revenue: pd.DataFrame,
) -> pd.DataFrame:
    """
    Identify calendar dates without recorded sales.

    Missing dates are reported rather than silently filled.
    """

    if daily_revenue.empty:
        raise ValueError(
            "Daily revenue dataset is empty."
        )

    full_range = pd.date_range(
        start=daily_revenue["date"].min(),
        end=daily_revenue["date"].max(),
        freq="D",
    )

    missing_dates = (
        full_range.difference(
            daily_revenue["date"]
        )
    )

    gap_report = pd.DataFrame(
        {
            "missing_date": missing_dates
        }
    )

    return gap_report


def save_forecasting_artifacts(
    daily_revenue: pd.DataFrame,
    gap_report: pd.DataFrame,
) -> None:
    """Save daily revenue and date-gap diagnostics."""

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    daily_path = (
        OUTPUT_DIR
        / "daily_revenue.csv"
    )

    gap_path = (
        OUTPUT_DIR
        / "date_gap_report.csv"
    )

    daily_revenue.to_csv(
        daily_path,
        index=False,
    )

    gap_report.to_csv(
        gap_path,
        index=False,
    )

    print(
        f"\nSaved daily revenue: {daily_path}"
    )

    print(
        f"Saved date-gap report: {gap_path}"
    )


def main() -> None:
    print("=" * 70)
    print("MARKETMINDAI - M2 DAY 5 DAILY REVENUE PIPELINE")
    print("=" * 70)

    # ---------------------------------------------------------
    # Load source data
    # ---------------------------------------------------------

    source_df = load_uci_online_retail()

    print(
        f"\nSource transactions: "
        f"{len(source_df):,}"
    )

    # ---------------------------------------------------------
    # Build daily time series
    # ---------------------------------------------------------

    daily_revenue = build_daily_revenue(
        source_df
    )

    print(
        f"Sales days available: "
        f"{len(daily_revenue):,}"
    )

    print(
        f"First date: "
        f"{daily_revenue['date'].min().date()}"
    )

    print(
        f"Last date: "
        f"{daily_revenue['date'].max().date()}"
    )

    # ---------------------------------------------------------
    # Validate date gaps
    # ---------------------------------------------------------

    gap_report = validate_date_gaps(
        daily_revenue
    )

    print(
        f"Days with no recorded sales: "
        f"{len(gap_report):,}"
    )

    # ---------------------------------------------------------
    # Save artifacts
    # ---------------------------------------------------------

    save_forecasting_artifacts(
        daily_revenue,
        gap_report,
    )

    print("\nSample daily revenue:")
    print(
        daily_revenue.head(10).to_string(
            index=False
        )
    )

    print(
        "\nM2 Day 5 daily revenue preparation completed."
    )


if __name__ == "__main__":
    main()