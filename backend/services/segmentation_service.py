import logging
from pathlib import Path

import pandas as pd


logger = logging.getLogger(__name__)


REQUIRED_COLUMNS = [
    "Customer ID",
    "purchase_frequency",
    "purchase_value",
    "last_purchase_date",
    "customer_activity_days",
    "cluster",
    "cluster_hierarchical",
    "segment_name",
]


def load_customer_segments(
    segmentation_file: Path,
) -> dict:
    """
    Load the completed customer segmentation artifact
    and prepare the API response data.

    The original artifact is never modified.
    """

    if not segmentation_file.exists():
        raise FileNotFoundError(
            "Customer segmentation artifact not found."
        )

    df = pd.read_csv(
        segmentation_file
    )

    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            "Segmentation artifact missing columns: "
            + str(missing_columns)
        )

    segment_summary = (
        df.groupby(
            "segment_name",
            dropna=False,
        )
        .agg(
            customer_count=(
                "Customer ID",
                "count",
            ),
            average_purchase_frequency=(
                "purchase_frequency",
                "mean",
            ),
            average_purchase_value=(
                "purchase_value",
                "mean",
            ),
            average_customer_activity_days=(
                "customer_activity_days",
                "mean",
            ),
        )
        .reset_index()
        .rename(
            columns={
                "segment_name": "segment"
            }
        )
    )

    for column in [
        "average_purchase_frequency",
        "average_purchase_value",
        "average_customer_activity_days",
    ]:
        segment_summary[column] = (
            segment_summary[column].round(2)
        )

    customers = (
        df[REQUIRED_COLUMNS]
        .where(
            pd.notnull(
                df[REQUIRED_COLUMNS]
            ),
            None,
        )
        .to_dict(
            orient="records"
        )
    )

    logger.info(
        "Customer segmentation artifact loaded successfully."
    )

    return {
        "total_customers": int(
            len(df)
        ),
        "segment_count": int(
            df[
                "segment_name"
            ].nunique()
        ),
        "segment_summary": (
            segment_summary
            .to_dict(
                orient="records"
            )
        ),
        "customers": customers,
    }