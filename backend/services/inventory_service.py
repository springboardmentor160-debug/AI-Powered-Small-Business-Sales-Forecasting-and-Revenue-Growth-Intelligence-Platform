import logging
from datetime import date

import pandas as pd
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.data_pipeline.sources.uci.loader import (
    read_uci_transactions,
)
from backend.models.inventory import Inventory
from backend.models.product import Product


logger = logging.getLogger(__name__)


def generate_inventory_preview(
    db: Session,
) -> dict:
    """
    Generate and persist estimated inventory from UCI sales.

    Formula:
        InitialStock = TotalUnitsSold × 1.5

    The latest valid UCI InvoiceDate is used as the
    inventory snapshot date.
    """

    df = read_uci_transactions()

    required_columns = [
        "StockCode",
        "Description",
        "Quantity",
        "InvoiceDate",
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

    df["InvoiceDate"] = pd.to_datetime(
        df["InvoiceDate"],
        errors="coerce",
    )

    sales_df = df[
        (df["Quantity"] > 0)
        & df["InvoiceDate"].notna()
    ].copy()

    if sales_df.empty:
        return {
            "total_products": 0,
            "total_units_sold": 0,
            "total_estimated_initial_stock": 0,
            "total_estimated_remaining_stock": 0,
            "products": [],
        }

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

    snapshot_date = (
        sales_df["InvoiceDate"].max().date()
    )

    # ---------------------------------------------------------
    # PostgreSQL product mapping
    # ---------------------------------------------------------

    # A StockCode represents one product in the PostgreSQL
    # product master, so select one reliable description
    # for each StockCode.
    product_master = (
        inventory[
            [
                "ProductID",
                "ProductDescription",
            ]
        ]
        .copy()
    )

    product_master["ProductID"] = (
        product_master["ProductID"]
        .astype(str)
    )

    product_master["ProductDescription"] = (
        product_master["ProductDescription"]
        .where(
            product_master["ProductDescription"]
            .notna()
        )
        .astype(str)
    )

    product_master.loc[
        product_master["ProductDescription"].isin(
            ["nan", "None", ""]
        ),
        "ProductDescription",
    ] = None

    # Prefer the first non-empty description for each
    # StockCode. This avoids duplicate Product rows.
    product_master = (
        product_master
        .sort_values(
            by=[
                "ProductID",
                "ProductDescription",
            ],
            na_position="last",
        )
        .drop_duplicates(
            subset=["ProductID"],
            keep="first",
        )
    )

    stock_codes = (
        product_master["ProductID"]
        .tolist()
    )

    products = db.scalars(
        select(Product).where(
            Product.stock_code.in_(stock_codes)
        )
    ).all()

    product_map = {
        product.stock_code: product.id
        for product in products
    }

    # Create missing products.
    missing_products = []

    for row in product_master.itertuples(
            index=False
    ):
        stock_code = str(row.ProductID)

        if stock_code in product_map:
            continue

        description = row.ProductDescription

        missing_products.append(
            Product(
                stock_code=stock_code,
                description=(
                    str(description)
                    if pd.notna(description)
                    else None
                ),
            )
        )

    if missing_products:
        db.add_all(missing_products)
        db.flush()

        for product in missing_products:
            product_map[
                product.stock_code
            ] = product.id

    # ---------------------------------------------------------
    # Persist inventory snapshot
    # ---------------------------------------------------------

    persisted = 0

    for row in inventory.itertuples(
        index=False
    ):
        stock_code = str(row.ProductID)

        product_id = product_map.get(
            stock_code
        )

        if product_id is None:
            continue

        existing = db.scalar(
            select(Inventory).where(
                Inventory.product_id == product_id,
                Inventory.inventory_date
                == snapshot_date,
            )
        )

        if existing:
            existing.initial_stock = float(
                row.InitialStock
            )
            existing.units_sold = float(
                row.TotalUnitsSold
            )
            existing.ending_stock = float(
                row.EstimatedRemainingStock
            )
        else:
            db.add(
                Inventory(
                    product_id=product_id,
                    store_code=None,
                    inventory_date=snapshot_date,
                    initial_stock=float(
                        row.InitialStock
                    ),
                    units_sold=float(
                        row.TotalUnitsSold
                    ),
                    ending_stock=float(
                        row.EstimatedRemainingStock
                    ),
                )
            )

        persisted += 1

    db.commit()

    records = (
        inventory
        .fillna("")
        .to_dict(orient="records")
    )

    logger.info(
        "Inventory snapshot persisted: %s products.",
        persisted,
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
            inventory[
                "EstimatedRemainingStock"
            ].sum()
        ),
        "products": records,
    }