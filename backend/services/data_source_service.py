import logging

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.models.data_source import DataSource

logger = logging.getLogger(__name__)


SOURCE_REGISTRY = [
    {
        "source_system": "UCI",
        "source_name": "UCI Online Retail II",
        "source_file": "online_retail_v1.csv",
        "source_version": "original",
        "source_type": "transaction",
        "description": (
            "Original UCI Online Retail II transaction source, "
            "version 1."
        ),
    },
    {
        "source_system": "UCI",
        "source_name": "UCI Online Retail II",
        "source_file": "online_retail_v2.csv",
        "source_version": "original",
        "source_type": "transaction",
        "description": (
            "Original UCI Online Retail II transaction source, "
            "version 2."
        ),
    },
    {
        "source_system": "M5",
        "source_name": "M5 Forecasting",
        "source_file": "sales_train_validation.csv",
        "source_version": "original",
        "source_type": "sales_history",
        "description": (
            "Original M5 historical sales validation source."
        ),
    },
    {
        "source_system": "M5",
        "source_name": "M5 Forecasting",
        "source_file": "sales_train_evaluation.csv",
        "source_version": "original",
        "source_type": "sales_history",
        "description": (
            "Original M5 historical sales evaluation source."
        ),
    },
    {
        "source_system": "M5",
        "source_name": "M5 Forecasting",
        "source_file": "calendar.csv",
        "source_version": "original",
        "source_type": "calendar",
        "description": (
            "Original M5 calendar and event source."
        ),
    },
    {
        "source_system": "M5",
        "source_name": "M5 Forecasting",
        "source_file": "sell_prices.csv",
        "source_version": "original",
        "source_type": "pricing",
        "description": (
            "Original M5 weekly sell-price source."
        ),
    },
]


def register_data_sources(
    db: Session,
) -> dict:
    inserted = 0
    existing = 0

    for source in SOURCE_REGISTRY:
        record = db.scalar(
            select(DataSource).where(
                DataSource.source_system
                == source["source_system"],
                DataSource.source_file
                == source["source_file"],
            )
        )

        if record:
            existing += 1
            continue

        db.add(
            DataSource(**source)
        )
        inserted += 1

    db.commit()

    logger.info(
        "Data source registry synchronized: "
        "inserted=%s, existing=%s",
        inserted,
        existing,
    )

    return {
        "inserted": inserted,
        "existing": existing,
        "total": inserted + existing,
    }