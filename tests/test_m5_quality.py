
from pathlib import Path

import pandas as pd
import pytest

from backend.data_pipeline.validation import m5_quality


def test_validate_schema_accepts_all_required_columns():
    for filename, expected_columns in m5_quality.EXPECTED_COLUMNS.items():
        m5_quality.validate_schema(filename, sorted(expected_columns))


def test_validate_schema_rejects_missing_columns():
    filename = "calendar.csv"
    columns = ["date", "weekday"]

    with pytest.raises(ValueError, match="missing expected columns"):
        m5_quality.validate_schema(filename, columns)


def test_validate_schema_allows_additional_columns():
    filename = "calendar.csv"
    columns = sorted(m5_quality.EXPECTED_COLUMNS[filename])
    columns.append("additional_column")

    m5_quality.validate_schema(filename, columns)


def test_validate_schema_rejects_unknown_filename():
    with pytest.raises((KeyError, ValueError)):
        m5_quality.validate_schema("unknown.csv", ["date"])


def test_inspect_schema_reads_header_and_sample(tmp_path):
    csv_path = tmp_path / "sample.csv"
    pd.DataFrame({
        "date": ["2025-01-01", "2025-01-02", "2025-01-03"],
        "units_sold": [10, 12, 15],
    }).to_csv(csv_path, index=False)

    row_count, columns = m5_quality.inspect_schema(csv_path)

    assert row_count == 3
    assert columns == ["date", "units_sold"]


def test_inspect_schema_reads_at_most_five_sample_rows(tmp_path):
    csv_path = tmp_path / "sample.csv"
    pd.DataFrame({
        "id": range(10),
        "value": range(10, 20),
    }).to_csv(csv_path, index=False)

    row_count, columns = m5_quality.inspect_schema(csv_path)

    assert row_count == 5
    assert columns == ["id", "value"]


def test_inspect_schema_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        m5_quality.inspect_schema(tmp_path / "missing.csv")


def test_validate_files_rejects_missing_source_files(monkeypatch, tmp_path):
    missing_paths = [
        tmp_path / "calendar.csv",
        tmp_path / "sales_train_validation.csv",
        tmp_path / "sales_train_evaluation.csv",
        tmp_path / "sell_prices.csv",
    ]

    monkeypatch.setattr(m5_quality, "CALENDAR_PATH", missing_paths[0])
    monkeypatch.setattr(m5_quality, "SALES_VALIDATION_PATH", missing_paths[1])
    monkeypatch.setattr(m5_quality, "SALES_EVALUATION_PATH", missing_paths[2])
    monkeypatch.setattr(m5_quality, "SELL_PRICES_PATH", missing_paths[3])

    with pytest.raises(FileNotFoundError, match="Missing M5 source files"):
        m5_quality.validate_files()
