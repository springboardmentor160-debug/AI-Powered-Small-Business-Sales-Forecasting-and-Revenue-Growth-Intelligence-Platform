from pathlib import Path

import pandas as pd


BACKEND_DIR = Path(__file__).resolve().parents[3]

M5_DATA_DIR = (
    BACKEND_DIR
    / "data"
    / "raw"
    / "m5"
)

CALENDAR_PATH = M5_DATA_DIR / "calendar.csv"
SALES_VALIDATION_PATH = (
    M5_DATA_DIR / "sales_train_validation.csv"
)
SALES_EVALUATION_PATH = (
    M5_DATA_DIR / "sales_train_evaluation.csv"
)
SELL_PRICES_PATH = (
    M5_DATA_DIR / "sell_prices.csv"
)


def validate_m5_files() -> None:
    """Verify that all required M5 source files exist."""

    required_files = [
        CALENDAR_PATH,
        SALES_VALIDATION_PATH,
        SALES_EVALUATION_PATH,
        SELL_PRICES_PATH,
    ]

    missing = [
        str(path)
        for path in required_files
        if not path.exists()
    ]

    if missing:
        raise FileNotFoundError(
            "Missing M5 source files:\n"
            + "\n".join(missing)
        )


def load_calendar() -> pd.DataFrame:
    validate_m5_files()
    return pd.read_csv(CALENDAR_PATH)


def load_sales_validation() -> pd.DataFrame:
    validate_m5_files()
    return pd.read_csv(SALES_VALIDATION_PATH)


def load_sales_evaluation() -> pd.DataFrame:
    validate_m5_files()
    return pd.read_csv(SALES_EVALUATION_PATH)


def load_sell_prices() -> pd.DataFrame:
    validate_m5_files()
    return pd.read_csv(SELL_PRICES_PATH)