from pathlib import Path

import pandas as pd

from backend.data_pipeline.sources.m5.loader import (
    CALENDAR_PATH,
    SALES_EVALUATION_PATH,
    SALES_VALIDATION_PATH,
    SELL_PRICES_PATH,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]

OUTPUT_DIR = (
    PROJECT_ROOT
    / "artifacts"
    / "milestone-2"
    / "forecasting"
)


EXPECTED_COLUMNS = {
    "calendar.csv": {
        "date",
        "wm_yr_wk",
        "weekday",
        "wday",
        "month",
        "year",
    },
    "sales_train_validation.csv": {
        "id",
        "item_id",
        "dept_id",
        "cat_id",
        "store_id",
        "state_id",
    },
    "sales_train_evaluation.csv": {
        "id",
        "item_id",
        "dept_id",
        "cat_id",
        "store_id",
        "state_id",
    },
    "sell_prices.csv": {
        "store_id",
        "item_id",
        "wm_yr_wk",
        "sell_price",
    },
}


def validate_files() -> None:
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


def inspect_schema(
    path: Path,
) -> tuple[int, list[str]]:
    """
    Read only the CSV header and a tiny sample.

    Large M5 files are intentionally not loaded completely
    during source validation.
    """

    header_df = pd.read_csv(
        path,
        nrows=0,
    )

    sample_df = pd.read_csv(
        path,
        nrows=5,
    )

    return len(sample_df), header_df.columns.tolist()


def validate_schema(
    filename: str,
    columns: list[str],
) -> None:
    """Check that required source columns exist."""

    expected = EXPECTED_COLUMNS[filename]

    missing = expected - set(columns)

    if missing:
        raise ValueError(
            f"{filename} is missing expected columns: "
            f"{sorted(missing)}"
        )


def main() -> None:
    print("=" * 75)
    print("MARKETMINDAI - M5 DATA SOURCE VALIDATION")
    print("=" * 75)

    validate_files()

    source_files = [
        ("calendar.csv", CALENDAR_PATH),
        (
            "sales_train_validation.csv",
            SALES_VALIDATION_PATH,
        ),
        (
            "sales_train_evaluation.csv",
            SALES_EVALUATION_PATH,
        ),
        ("sell_prices.csv", SELL_PRICES_PATH),
    ]

    validation_results = []

    for filename, path in source_files:

        sample_rows, columns = inspect_schema(path)

        validate_schema(
            filename,
            columns,
        )

        size_mb = path.stat().st_size / (
            1024 * 1024
        )

        validation_results.append(
            {
                "file": filename,
                "size_mb": round(size_mb, 2),
                "column_count": len(columns),
                "sample_rows_read": sample_rows,
                "schema_status": "PASS",
            }
        )

        print(f"\n{filename}")
        print(f"  Size: {size_mb:.2f} MB")
        print(f"  Columns: {len(columns)}")
        print(f"  Schema: PASS")

        print(
            "  First columns:",
            columns[:10],
        )

        print(
            "  Last columns:",
            columns[-5:],
        )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    report_path = (
        OUTPUT_DIR
        / "m5_source_validation.csv"
    )

    pd.DataFrame(
        validation_results
    ).to_csv(
        report_path,
        index=False,
    )

    print(
        f"\nSaved validation report: "
        f"{report_path}"
    )

    print(
        "\nM5 data source validation completed successfully."
    )


if __name__ == "__main__":
    main()