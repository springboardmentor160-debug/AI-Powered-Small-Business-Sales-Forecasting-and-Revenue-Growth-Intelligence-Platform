import logging

import pandas as pd

from backend.data_pipeline.sources.uci.loader import (
    read_uci_transactions,
)

logger = logging.getLogger(__name__)


def generate_inventory_preview() -> dict:
    """
    Generate estimated inventory from
    the original UCI source files.

    Formula:

        InitialStock =
            TotalUnitsSold × 1.5

    Raw UCI files are read only.
    """

    df = read_uci_transactions()

    required_columns = [
        "StockCode",
        "Description",
        "Quantity",
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            "Missing required inventory columns: "
            + str(missing_columns)
        )

    df["Quantity"] = pd.to_numeric(
        df["Quantity"],
        errors="coerce",
    )

    sales_df = df[
        df["Quantity"] > 0
    ].copy()

    inventory = (
        sales_df
        .groupby(
            [
                "StockCode",
                "Description",
            ],
            dropna=False,
        )
        .agg(
            TotalUnitsSold=(
                "Quantity",
                "sum",
            )
        )
        .reset_index()
        .rename(
            columns={
                "StockCode": "ProductID",
                "Description": "ProductDescription",
            }
        )
    )

    inventory["InitialStock"] = (
        inventory["TotalUnitsSold"] * 1.5
    ).round().astype("int64")

    inventory["EstimatedRemainingStock"] = (
        inventory["InitialStock"]
        - inventory["TotalUnitsSold"]
    ).clip(
        lower=0
    ).round().astype("int64")

    records = (
        inventory
        .fillna("")
        .to_dict(orient="records")
    )
    return {
        "total_products": len(records),
        "total_units_sold": int(
            inventory["TotalUnitsSold"].sum()
        ),
        "total_estimated_initial_stock": int(
            inventory["InitialStock"].sum()
        ),
        "total_estimated_remaining_stock": int(
            inventory["EstimatedRemainingStock"].sum()
        ),
        "products": records,
    }