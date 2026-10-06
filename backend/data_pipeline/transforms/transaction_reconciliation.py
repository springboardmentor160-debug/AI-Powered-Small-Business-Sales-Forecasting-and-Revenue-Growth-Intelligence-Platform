import numpy as np
import pandas as pd


REQUIRED_COLUMNS = {
    "Invoice",
    "StockCode",
    "Description",
    "Quantity",
    "InvoiceDate",
    "Price",
    "Customer ID",
    "Country",
}


def reconcile_invoice_reversals(
    sales_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Reconcile complete invoice-level cancellations.

    The original source dataframe is never modified.

    A positive invoice is considered reversed when a later
    cancellation invoice for the same customer has the exact
    opposite invoice total.

    Matching criteria:
        - same customer
        - equal absolute invoice total
        - cancellation occurs after the positive invoice

    The closest preceding matching invoice is selected.
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

    df["_row_id"] = np.arange(len(df))

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

    df["is_reversal"] = False

    df["reversal_match_invoice"] = pd.Series(
        pd.NA,
        index=df.index,
        dtype="object",
    )

    # ---------------------------------------------------------
    # Build invoice-level totals
    # ---------------------------------------------------------

    invoice_summary = (
        df[
            df["Customer ID"].notna()
            & df["InvoiceDate"].notna()
        ]
        .groupby(
            [
                "Customer ID",
                "Invoice",
            ],
            as_index=False,
        )
        .agg(
            invoice_date=(
                "InvoiceDate",
                "min",
            ),
            invoice_total=(
                "total_amount",
                "sum",
            ),
        )
    )

    invoice_summary["is_cancellation_invoice"] = (
        invoice_summary["Invoice"]
        .str.upper()
        .str.startswith("C")
    )

    # ---------------------------------------------------------
    # Candidate positive invoices
    # ---------------------------------------------------------

    positive_invoices = invoice_summary[
        (~invoice_summary["is_cancellation_invoice"])
        & (invoice_summary["invoice_total"] > 0)
    ].copy()

    # ---------------------------------------------------------
    # Candidate cancellation invoices
    # ---------------------------------------------------------

    cancellation_invoices = invoice_summary[
        invoice_summary["is_cancellation_invoice"]
        & (invoice_summary["invoice_total"] < 0)
    ].copy()

    if (
        positive_invoices.empty
        or cancellation_invoices.empty
    ):
        return df

    positive_invoices["matching_amount"] = (
        positive_invoices["invoice_total"].round(2)
    )

    cancellation_invoices["matching_amount"] = (
        cancellation_invoices["invoice_total"]
        .abs()
        .round(2)
    )

    # ---------------------------------------------------------
    # Match cancellation invoices against earlier invoices
    # ---------------------------------------------------------

    candidates = cancellation_invoices.merge(
        positive_invoices,
        on=[
            "Customer ID",
            "matching_amount",
        ],
        suffixes=(
            "_cancellation",
            "_positive",
        ),
    )

    candidates = candidates[
        candidates["invoice_date_positive"]
        <= candidates["invoice_date_cancellation"]
    ].copy()

    if candidates.empty:
        return df

    candidates["time_difference"] = (
        candidates["invoice_date_cancellation"]
        - candidates["invoice_date_positive"]
    )

    candidates = candidates.sort_values(
        [
            "Invoice_cancellation",
            "time_difference",
        ]
    )

    used_positive_invoices = set()
    used_cancellation_invoices = set()

    matches = []

    for row in candidates.itertuples(index=False):

        positive_invoice = row.Invoice_positive
        cancellation_invoice = row.Invoice_cancellation

        if (
            positive_invoice
            in used_positive_invoices
        ):
            continue

        if (
            cancellation_invoice
            in used_cancellation_invoices
        ):
            continue

        used_positive_invoices.add(
            positive_invoice
        )

        used_cancellation_invoices.add(
            cancellation_invoice
        )

        matches.append(
            (
                positive_invoice,
                cancellation_invoice,
            )
        )

    # ---------------------------------------------------------
    # Mark matched invoice rows
    # ---------------------------------------------------------

    for (
        positive_invoice,
        cancellation_invoice,
    ) in matches:

        positive_mask = (
            df["Invoice"]
            == str(positive_invoice)
        )

        cancellation_mask = (
            df["Invoice"]
            == str(cancellation_invoice)
        )

        df.loc[
            positive_mask,
            "is_reversal",
        ] = True

        df.loc[
            cancellation_mask,
            "is_reversal",
        ] = True

        df.loc[
            positive_mask,
            "reversal_match_invoice",
        ] = str(cancellation_invoice)

        df.loc[
            cancellation_mask,
            "reversal_match_invoice",
        ] = str(positive_invoice)

    return df


def main() -> None:
    """
    Run an invoice-level reconciliation diagnostic.
    """

    from backend.data_pipeline.sources.uci.loader import (
        load_uci_online_retail,
    )

    print("=" * 70)
    print("MARKETMINDAI - INVOICE REVERSAL RECONCILIATION")
    print("=" * 70)

    source_df = load_uci_online_retail()

    reconciled_df = reconcile_invoice_reversals(
        source_df
    )

    reversal_rows = reconciled_df[
        reconciled_df["is_reversal"]
    ]

    positive_reversal_rows = reversal_rows[
        reversal_rows["Quantity"] > 0
    ]

    cancellation_rows = reversal_rows[
        reversal_rows["Quantity"] < 0
    ]

    print(
        f"\nTotal source rows: "
        f"{len(source_df):,}"
    )

    print(
        f"Reconciled reversal rows: "
        f"{len(reversal_rows):,}"
    )

    print(
        f"Positive rows belonging to reversed invoices: "
        f"{len(positive_reversal_rows):,}"
    )

    print(
        f"Cancellation rows matched: "
        f"{len(cancellation_rows):,}"
    )

    print(
        f"Customers affected: "
        f"{reversal_rows['Customer ID'].nunique():,}"
    )

    print("\nCustomer 16446:")
    print(
        reconciled_df[
            reconciled_df["Customer ID"] == 16446.0
        ][
            [
                "Invoice",
                "StockCode",
                "Quantity",
                "Price",
                "InvoiceDate",
                "total_amount",
                "is_reversal",
                "reversal_match_invoice",
            ]
        ].to_string(index=False)
    )

    print("\nCustomer 15098:")
    print(
        reconciled_df[
            reconciled_df["Customer ID"] == 15098.0
        ][
            [
                "Invoice",
                "StockCode",
                "Quantity",
                "Price",
                "InvoiceDate",
                "total_amount",
                "is_reversal",
                "reversal_match_invoice",
            ]
        ].to_string(index=False)
    )

    print("\nInvoice reconciliation completed.")


if __name__ == "__main__":
    main()