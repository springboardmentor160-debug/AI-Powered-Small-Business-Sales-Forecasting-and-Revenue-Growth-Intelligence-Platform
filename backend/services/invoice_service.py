import json
import logging

from backend.config import (
    INVOICE_DATA_DIR,
    INVOICE_FILE,
)

logger = logging.getLogger(__name__)


def load_invoice_records() -> list[dict]:
    """
    Load invoices from the persistent JSON registry.

    The invoice registry is separate from the raw UCI/M5 datasets.
    """

    INVOICE_DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    if not INVOICE_FILE.exists():
        return []

    try:
        with INVOICE_FILE.open(
            "r",
            encoding="utf-8",
        ) as file:
            data = json.load(file)

        if isinstance(data, list):
            return data

        return []

    except (
        json.JSONDecodeError,
        OSError,
    ) as error:
        logger.error(
            "Unable to load invoice registry: %s",
            error,
        )

        return []


def save_invoice_records(
    records: list[dict],
) -> None:
    """
    Persist invoice records safely.

    A temporary file is written first and then replaced.
    """

    INVOICE_DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    temporary_file = (
        INVOICE_FILE.with_suffix(".tmp")
    )

    with temporary_file.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            records,
            file,
            indent=2,
            ensure_ascii=False,
        )

    temporary_file.replace(
        INVOICE_FILE
    )