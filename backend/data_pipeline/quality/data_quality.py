from pathlib import Path

import pandas as pd


def validate_required_columns(
    df: pd.DataFrame,
    required_columns: set[str],
    dataset_name: str,
) -> list[str]:
    """Return required columns that are missing from a dataset."""
    missing = sorted(required_columns - set(df.columns))

    if missing:
        return [
            f"{dataset_name}: missing columns: {missing}"
        ]

    return []


def validate_missing_values(
    df: pd.DataFrame,
    dataset_name: str,
    allowed_null_columns: set[str] | None = None,
) -> dict:
    """
    Validate missing values while allowing explicitly approved null columns.
    """
    allowed_null_columns = allowed_null_columns or set()

    missing_counts = (
        df.isna()
        .sum()
        .loc[lambda series: series > 0]
        .to_dict()
    )

    allowed_missing = {
        column: int(count)
        for column, count in missing_counts.items()
        if column in allowed_null_columns
    }

    unexpected_missing = {
        column: int(count)
        for column, count in missing_counts.items()
        if column not in allowed_null_columns
    }

    return {
        "dataset": dataset_name,
        "allowed_null_columns": sorted(
            allowed_null_columns
        ),
        "allowed_missing_values": allowed_missing,
        "unexpected_missing_values": unexpected_missing,
        "total_missing_values": int(
            sum(missing_counts.values())
        ),
        "total_unexpected_missing_values": int(
            sum(unexpected_missing.values())
        ),
    }


def validate_numeric_columns(
    df: pd.DataFrame,
    numeric_columns: set[str],
    dataset_name: str,
) -> list[str]:
    """Validate that required numeric columns can be interpreted as numeric."""
    errors = []

    for column in sorted(numeric_columns):
        if column not in df.columns:
            continue

        converted = pd.to_numeric(
            df[column],
            errors="coerce",
        )

        invalid_count = int(
            converted.isna().sum()
            - df[column].isna().sum()
        )

        if invalid_count > 0:
            errors.append(
                f"{dataset_name}: column '{column}' "
                f"contains {invalid_count} non-numeric values."
            )

    return errors


def build_quality_report(
    df: pd.DataFrame,
    dataset_name: str,
    required_columns: set[str],
    numeric_columns: set[str],
    allowed_null_columns: set[str] | None = None,
) -> dict:
    """Build a structural and data-quality report."""

    schema_errors = validate_required_columns(
        df,
        required_columns,
        dataset_name,
    )

    numeric_errors = validate_numeric_columns(
        df,
        numeric_columns,
        dataset_name,
    )

    missing_report = validate_missing_values(
        df,
        dataset_name,
        allowed_null_columns,
    )

    duplicate_rows = int(
        df.duplicated().sum()
    )

    unexpected_missing = (
        missing_report[
            "total_unexpected_missing_values"
        ]
    )

    status = "PASS"

    if schema_errors or numeric_errors:
        status = "FAIL"
    elif unexpected_missing > 0 or duplicate_rows > 0:
        status = "WARNING"

    return {
        "dataset": dataset_name,
        "row_count": int(len(df)),
        "column_count": int(len(df.columns)),
        "schema_errors": schema_errors,
        "numeric_errors": numeric_errors,
        "missing_values": missing_report,
        "duplicate_rows": duplicate_rows,
        "status": status,
    }


def load_csv(path: Path) -> pd.DataFrame:
    """Load a CSV file without modifying the source file."""
    if not path.exists():
        raise FileNotFoundError(
            f"Dataset not found: {path}"
        )

    return pd.read_csv(path)


def save_quality_report(
    report: dict,
    output_path: Path,
) -> None:
    """Save a quality report as a JSON artifact."""
    import json

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with output_path.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            report,
            file,
            indent=2,
        )