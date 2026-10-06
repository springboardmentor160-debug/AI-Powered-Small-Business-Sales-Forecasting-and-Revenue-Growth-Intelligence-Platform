import pandas as pd

from backend.data_pipeline.transforms.transaction_reconciliation import (
    reconcile_invoice_reversals,
)


REQUIRED_COLUMNS = {
    "Invoice",
    "Quantity",
    "InvoiceDate",
    "Price",
    "Customer ID",
}


def build_customer_features(
    sales_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Build customer-level behavioral features.

    Features:
        purchase_frequency
        purchase_value
        customer_activity_days

    Feature definitions:
        purchase_frequency:
            Number of completed positive-value invoices.

        purchase_value:
            Average completed invoice value.

        customer_activity_days:
            Days since the customer's most recent
            completed invoice.

    Raw source data is never modified.
    """

    missing_columns = (
        REQUIRED_COLUMNS - set(sales_df.columns)
    )

    if missing_columns:
        raise ValueError(
            f"Missing required columns: "
            f"{sorted(missing_columns)}"
        )

    df = sales_df.copy()

    # ---------------------------------------------------------
    # Normalize types
    # ---------------------------------------------------------

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

    # ---------------------------------------------------------
    # Reconcile complete invoice reversals
    # ---------------------------------------------------------

    df = reconcile_invoice_reversals(df)

    # ---------------------------------------------------------
    # Keep valid completed sales invoices
    # ---------------------------------------------------------

    eligible_rows = (
        df["Customer ID"].notna()
        & df["InvoiceDate"].notna()
        & (~df["Invoice"].str.upper().str.startswith("C"))
        & (~df["is_reversal"])
    )

    sales_df = df.loc[
        eligible_rows
    ].copy()

    if sales_df.empty:
        raise ValueError(
            "No completed sales available "
            "for customer segmentation."
        )

    # ---------------------------------------------------------
    # Aggregate transaction lines to invoice level
    # ---------------------------------------------------------

    invoice_features = (
        sales_df
        .groupby(
            [
                "Customer ID",
                "Invoice",
            ],
            as_index=False,
        )
        .agg(
            invoice_total=(
                "total_amount",
                "sum",
            ),
            invoice_date=(
                "InvoiceDate",
                "max",
            ),
        )
    )

    # Only positive completed invoices become purchases.
    invoice_features = invoice_features[
        invoice_features["invoice_total"] > 0
    ].copy()

    if invoice_features.empty:
        raise ValueError(
            "No positive completed invoices "
            "available for segmentation."
        )

    # ---------------------------------------------------------
    # Reproducible analysis date
    # ---------------------------------------------------------

    analysis_date = (
        invoice_features["invoice_date"]
        .max()
        .normalize()
        + pd.Timedelta(days=1)
    )

    # ---------------------------------------------------------
    # Customer-level aggregation
    # ---------------------------------------------------------

    customer_features = (
        invoice_features
        .groupby("Customer ID")
        .agg(
            purchase_frequency=(
                "Invoice",
                "nunique",
            ),
            purchase_value=(
                "invoice_total",
                "mean",
            ),
            last_purchase_date=(
                "invoice_date",
                "max",
            ),
        )
        .reset_index()
    )

    # ---------------------------------------------------------
    # Customer activity
    # ---------------------------------------------------------

    customer_features[
        "customer_activity_days"
    ] = (
        analysis_date
        - customer_features[
            "last_purchase_date"
        ].dt.normalize()
    ).dt.days

    return customer_features