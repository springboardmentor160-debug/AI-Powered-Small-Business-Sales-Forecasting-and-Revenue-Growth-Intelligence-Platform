import logging

import pandas as pd
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.models.customer import Customer
from backend.models.product import Product
from backend.models.sale import Sale


logger = logging.getLogger(__name__)


BATCH_SIZE = 5000


def persist_uci_transactions(
    db: Session,
    df: pd.DataFrame,
) -> dict:
    """
    Persist UCI transactions into PostgreSQL using batched operations.

    The operation is idempotent through the combination of
    source_system and source_row_id.

    The input dataframe is never modified.
    """

    required_columns = {
        "Invoice",
        "StockCode",
        "Description",
        "Quantity",
        "InvoiceDate",
        "Price",
        "Customer ID",
        "Country",
    }

    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        raise ValueError(
            "UCI dataset missing columns: "
            + str(missing_columns)
        )

    if "_source_row_id" not in df.columns:
        raise ValueError(
            "UCI dataframe is missing _source_row_id."
        )

    working_df = df.copy()

    working_df["Invoice"] = working_df["Invoice"].astype(str)
    working_df["StockCode"] = working_df["StockCode"].astype(str)

    working_df["Quantity"] = pd.to_numeric(
        working_df["Quantity"],
        errors="coerce",
    )

    working_df["Price"] = pd.to_numeric(
        working_df["Price"],
        errors="coerce",
    )

    working_df["InvoiceDate"] = pd.to_datetime(
        working_df["InvoiceDate"],
        errors="coerce",
    )

    working_df = working_df.dropna(
        subset=[
            "Invoice",
            "StockCode",
            "Quantity",
            "Price",
            "InvoiceDate",
        ]
    )

    working_df = working_df[
        (working_df["Quantity"] > 0)
        & (working_df["Price"] > 0)
    ].copy()

    if working_df.empty:
        return {
            "customers": 0,
            "products": 0,
            "sales": 0,
            "skipped": 0,
        }

    # ---------------------------------------------------------
    # Existing source rows
    # ---------------------------------------------------------

    source_row_ids = (
        working_df["_source_row_id"]
        .astype(int)
        .tolist()
    )

    existing_source_rows = set()

    for start in range(
        0,
        len(source_row_ids),
        BATCH_SIZE,
    ):
        batch_ids = source_row_ids[
            start:start + BATCH_SIZE
        ]

        existing_source_rows.update(
            db.scalars(
                select(Sale.source_row_id).where(
                    Sale.source_system == "UCI",
                    Sale.source_row_id.in_(batch_ids),
                )
            ).all()
        )

    new_df = working_df[
        ~working_df["_source_row_id"].isin(
            existing_source_rows
        )
    ].copy()

    skipped_sales = (
        len(working_df) - len(new_df)
    )

    if new_df.empty:
        return {
            "customers": 0,
            "products": 0,
            "sales": 0,
            "skipped": skipped_sales,
        }

    # ---------------------------------------------------------
    # Customer lookup
    # ---------------------------------------------------------

    customer_ids = (
        new_df["Customer ID"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    customer_map: dict[str, int] = {}

    for start in range(
        0,
        len(customer_ids),
        BATCH_SIZE,
    ):
        batch_ids = customer_ids[
            start:start + BATCH_SIZE
        ]

        customers = db.scalars(
            select(Customer).where(
                Customer.customer_id.in_(batch_ids)
            )
        ).all()

        for customer in customers:
            customer_map[
                customer.customer_id
            ] = customer.id

    existing_customer_ids = set(
        customer_map.keys()
    )

    customer_rows = (
        new_df[
            ["Customer ID", "Country"]
        ]
        .dropna(subset=["Customer ID"])
        .drop_duplicates(subset=["Customer ID"])
    )

    new_customers = []

    for row in customer_rows.itertuples(
        index=False
    ):
        customer_id = str(row[0])

        if customer_id in existing_customer_ids:
            continue

        new_customers.append(
            Customer(
                customer_id=customer_id,
                country=(
                    str(row[1])
                    if pd.notna(row[1])
                    else None
                ),
            )
        )

    if new_customers:
        db.add_all(new_customers)
        db.flush()

        for customer in new_customers:
            customer_map[
                customer.customer_id
            ] = customer.id

    # ---------------------------------------------------------
    # Product lookup
    # ---------------------------------------------------------

    stock_codes = (
        new_df["StockCode"]
        .astype(str)
        .unique()
        .tolist()
    )

    product_map: dict[str, int] = {}

    for start in range(
        0,
        len(stock_codes),
        BATCH_SIZE,
    ):
        batch_codes = stock_codes[
            start:start + BATCH_SIZE
        ]

        products = db.scalars(
            select(Product).where(
                Product.stock_code.in_(batch_codes)
            )
        ).all()

        for product in products:
            product_map[
                product.stock_code
            ] = product.id

    existing_stock_codes = set(
        product_map.keys()
    )

    product_rows = (
        new_df[
            ["StockCode", "Description"]
        ]
        .drop_duplicates(subset=["StockCode"])
    )

    new_products = []

    for row in product_rows.itertuples(
        index=False
    ):
        stock_code = str(row[0])

        if stock_code in existing_stock_codes:
            continue

        new_products.append(
            Product(
                stock_code=stock_code,
                description=(
                    str(row[1])
                    if pd.notna(row[1])
                    else None
                ),
            )
        )

    if new_products:
        db.add_all(new_products)
        db.flush()

        for product in new_products:
            product_map[
                product.stock_code
            ] = product.id

    # ---------------------------------------------------------
    # Sales preparation
    # ---------------------------------------------------------

    sales_records = []

    for row in new_df.itertuples(
        index=False
    ):
        customer_id = None

        if pd.notna(row[6]):
            customer_id = customer_map.get(
                str(row[6])
            )

        product_id = product_map.get(
            str(row[1])
        )

        if product_id is None:
            skipped_sales += 1
            continue

        sales_records.append(
            {
                "source_system": "UCI",
                "source_row_id": int(row[-1]),
                "invoice": str(row[0]),
                "customer_id": customer_id,
                "product_id": product_id,
                "quantity": int(row[3]),
                "price": float(row[5]),
                "invoice_date": row[4].to_pydatetime(),
            }
        )

    # ---------------------------------------------------------
    # Batched sales insert
    # ---------------------------------------------------------

    for start in range(
        0,
        len(sales_records),
        BATCH_SIZE,
    ):
        batch = sales_records[
            start:start + BATCH_SIZE
        ]

        db.add_all(
            [
                Sale(**record)
                for record in batch
            ]
        )

        db.flush()

    db.commit()

    persisted_sales = len(sales_records)

    logger.info(
        (
            "UCI persistence completed: "
            "%s customers, %s products, "
            "%s sales persisted, %s sales skipped."
        ),
        len(customer_map),
        len(product_map),
        persisted_sales,
        skipped_sales,
    )

    return {
        "customers": len(customer_map),
        "products": len(product_map),
        "sales": persisted_sales,
        "skipped": skipped_sales,
    }