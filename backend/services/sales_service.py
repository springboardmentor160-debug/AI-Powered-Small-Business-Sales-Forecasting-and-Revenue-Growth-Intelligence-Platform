import logging

import pandas as pd


logger = logging.getLogger(__name__)


def prepare_sales_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Prepare UCI transaction data for sales analytics.

    The original dataframe is not modified.
    """

    required_columns = {
        "Invoice",
        "Quantity",
        "Price",
        "Description",
    }

    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        raise ValueError(
            "UCI dataset missing columns: "
            + str(missing_columns)
        )

    working_df = df.dropna(
        subset=[
            "Quantity",
            "Price",
            "Description",
        ]
    ).drop_duplicates().copy()

    working_df["Invoice"] = (
        working_df["Invoice"]
        .astype(str)
    )

    working_df["Quantity"] = pd.to_numeric(
        working_df["Quantity"],
        errors="coerce",
    )

    working_df["Price"] = pd.to_numeric(
        working_df["Price"],
        errors="coerce",
    )

    working_df = working_df[
        ~working_df["Invoice"].str.startswith(
            "C",
            na=True,
        )
        & (working_df["Quantity"] > 0)
        & (working_df["Price"] > 0)
    ].copy()

    working_df["Revenue"] = (
        working_df["Quantity"]
        * working_df["Price"]
    )

    return working_df


def calculate_sales_analytics(
    df: pd.DataFrame,
) -> dict:
    """
    Calculate executive sales analytics.
    """

    working_df = prepare_sales_data(df)

    if working_df.empty:
        return {
            "total_revenue": 0.0,
            "total_orders": 0,
            "top_product": "N/A",
        }

    analytics = {
        "total_revenue": round(
            float(
                working_df["Revenue"].sum()
            ),
            2,
        ),
        "total_orders": int(
            working_df["Invoice"].nunique()
        ),
        "top_product": "N/A",
    }

    analytics["top_product"] = str(
        working_df.groupby(
            "Description"
        )["Quantity"]
        .sum()
        .idxmax()
    )

    logger.info(
        "Sales analytics calculated successfully."
    )

    return analytics