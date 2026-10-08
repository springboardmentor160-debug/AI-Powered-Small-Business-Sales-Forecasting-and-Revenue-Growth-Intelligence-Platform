"""
MarketMindAI - M5 Demand Transformation
----------------------------------------
Creates a forecasting-ready daily demand series from the M5 dataset.

Design:
- Uses sales_train_validation.csv as the historical source.
- Finds the highest-volume item/store series without loading the entire
  dataset into memory at once.
- Converts d_1 ... d_1913 into one row per day.
- Enriches demand with calendar date and weekly sell price.
- Preserves the raw M5 files unchanged.
"""

from pathlib import Path

import pandas as pd

from backend.data_pipeline.sources.m5.loader import (
    SALES_VALIDATION_PATH,
    CALENDAR_PATH,
    SELL_PRICES_PATH,
    validate_m5_files,
)


# ---------------------------------------------------------------------
# PROJECT PATHS
# ---------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

OUTPUT_DIR = (
    PROJECT_ROOT
    / "artifacts"
    / "milestone-2"
    / "forecasting"
)

OUTPUT_PATH = OUTPUT_DIR / "m5_demand_sample.csv"


# ---------------------------------------------------------------------
# CONSTANTS
# ---------------------------------------------------------------------

ID_COLUMNS = [
    "id",
    "item_id",
    "dept_id",
    "cat_id",
    "store_id",
    "state_id",
]

DAY_PREFIX = "d_"


# ---------------------------------------------------------------------
# STEP 1: FIND HIGHEST-VOLUME ITEM/STORE SERIES
# ---------------------------------------------------------------------

def find_top_series():
    """
    Scan the M5 validation sales file in chunks and identify the
    item/store series with the highest total historical units sold.

    The full wide dataset is never kept in memory.
    """

    best_total_units = -1
    best_row = None

    print("\nScanning M5 sales data for highest-volume series...")

    for chunk_number, chunk in enumerate(
        pd.read_csv(
            SALES_VALIDATION_PATH,
            chunksize=1000,
            low_memory=False,
        ),
        start=1,
    ):

        day_columns = [
            column
            for column in chunk.columns
            if column.startswith(DAY_PREFIX)
        ]

        # Calculate historical units sold for each item/store series.
        totals = chunk[day_columns].sum(axis=1)

        local_index = totals.idxmax()
        local_total = totals.loc[local_index]

        if local_total > best_total_units:
            best_total_units = local_total
            best_row = chunk.loc[local_index].copy()

        if chunk_number % 10 == 0:
            print(f"  Processed chunks: {chunk_number}")

    if best_row is None:
        raise RuntimeError("Unable to identify an M5 demand series.")

    print("\nTop historical-demand series identified:")
    print(f"  ID: {best_row['id']}")
    print(f"  Item: {best_row['item_id']}")
    print(f"  Store: {best_row['store_id']}")
    print(f"  Department: {best_row['dept_id']}")
    print(f"  Category: {best_row['cat_id']}")
    print(f"  State: {best_row['state_id']}")
    print(f"  Total units sold: {best_total_units:,.0f}")

    return best_row


# ---------------------------------------------------------------------
# STEP 2: CONVERT d_1 ... d_1913 INTO DAILY ROWS
# ---------------------------------------------------------------------

def transform_to_daily_demand(best_row):
    """
    Convert the selected M5 wide series into a daily long-format dataset.
    """

    day_columns = [
        column
        for column in best_row.index
        if str(column).startswith(DAY_PREFIX)
    ]

    demand_df = pd.DataFrame(
        {
            "d": day_columns,
            "units_sold": [
                best_row[column]
                for column in day_columns
            ],
        }
    )

    # Add product/store metadata.
    for column in ID_COLUMNS:
        demand_df[column] = best_row[column]
    demand_df["_source_system"] = "M5"
    demand_df["_source_sales_file"] = SALES_VALIDATION_PATH.name
    demand_df["_source_calendar_file"] = CALENDAR_PATH.name
    demand_df["_source_price_file"] = SELL_PRICES_PATH.name
    return demand_df


# ---------------------------------------------------------------------
# STEP 3: MERGE CALENDAR
# ---------------------------------------------------------------------

def enrich_with_calendar(demand_df):
    """
    Map M5 day IDs to actual dates and calendar attributes.
    """

    calendar = pd.read_csv(CALENDAR_PATH)

    calendar_columns = [
        "d",
        "date",
        "wm_yr_wk",
        "weekday",
        "wday",
        "month",
        "year",
        "event_name_1",
        "event_type_1",
        "event_name_2",
        "event_type_2",
        "snap_CA",
        "snap_TX",
        "snap_WI",
    ]

    calendar = calendar[
        [
            column
            for column in calendar_columns
            if column in calendar.columns
        ]
    ]

    demand_df = demand_df.merge(
        calendar,
        on="d",
        how="left",
        validate="many_to_one",
    )

    return demand_df


# ---------------------------------------------------------------------
# STEP 4: MERGE SELL PRICE
# ---------------------------------------------------------------------

def enrich_with_prices(demand_df):
    """
    Add the corresponding weekly sell price for the item/store series.
    """

    prices = pd.read_csv(
        SELL_PRICES_PATH,
        usecols=[
            "store_id",
            "item_id",
            "wm_yr_wk",
            "sell_price",
        ],
    )

    demand_df = demand_df.merge(
        prices,
        on=[
            "store_id",
            "item_id",
            "wm_yr_wk",
        ],
        how="left",
        validate="many_to_one",
    )

    return demand_df


# ---------------------------------------------------------------------
# STEP 5: VALIDATE TRANSFORMED DATA
# ---------------------------------------------------------------------

def validate_demand_dataset(demand_df):
    """
    Run basic structural and forecasting-readiness checks.
    """

    print("\n" + "=" * 75)
    print("M5 DAILY DEMAND VALIDATION")
    print("=" * 75)

    print(f"Rows: {len(demand_df):,}")
    print(f"Columns: {len(demand_df.columns)}")

    print(
        f"Date range: "
        f"{demand_df['date'].min()} → {demand_df['date'].max()}"
    )

    print(
        f"Total units sold: "
        f"{demand_df['units_sold'].sum():,.0f}"
    )

    missing_dates = demand_df["date"].isna().sum()
    missing_prices = demand_df["sell_price"].isna().sum()

    print(f"Missing calendar dates: {missing_dates:,}")
    print(f"Missing sell prices: {missing_prices:,}")

    duplicate_keys = demand_df.duplicated(
        subset=["item_id", "store_id", "date"]
    ).sum()

    print(
        f"Duplicate item/store/date rows: "
        f"{duplicate_keys:,}"
    )

    # Convert date for final output.
    demand_df["date"] = pd.to_datetime(
        demand_df["date"],
        errors="coerce",
    )

    if missing_dates == 0:
        print("Calendar mapping: PASS")
    else:
        print("Calendar mapping: CHECK")

    if duplicate_keys == 0:
        print("Daily uniqueness: PASS")
    else:
        print("Daily uniqueness: CHECK")

    return demand_df


# ---------------------------------------------------------------------
# STEP 6: SAVE
# ---------------------------------------------------------------------

def save_output(demand_df):
    """
    Save the transformed M5 demand series.
    """

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    demand_df = demand_df.sort_values(
        by="date"
    ).reset_index(drop=True)

    demand_df.to_csv(
        OUTPUT_PATH,
        index=False,
    )

    print(
        f"\nSaved transformed M5 demand dataset:\n"
        f"{OUTPUT_PATH}"
    )


# ---------------------------------------------------------------------
# MAIN PIPELINE
# ---------------------------------------------------------------------

def main():

    print("=" * 75)
    print("MARKETMINDAI - M5 DEMAND TRANSFORMATION")
    print("=" * 75)

    # Confirm raw source files exist.
    validate_m5_files()

    # Find one real, high-volume item/store demand series.
    best_row = find_top_series()

    # Wide -> long transformation.
    demand_df = transform_to_daily_demand(best_row)

    # Add calendar information.
    demand_df = enrich_with_calendar(demand_df)

    # Add weekly selling price.
    demand_df = enrich_with_prices(demand_df)

    # Validate the final forecasting-ready series.
    demand_df = validate_demand_dataset(demand_df)

    # Save artifact.
    save_output(demand_df)

    print("\nM5 demand transformation completed successfully.")


# ---------------------------------------------------------------------
# ENTRY POINT
# ---------------------------------------------------------------------

if __name__ == "__main__":
    main()