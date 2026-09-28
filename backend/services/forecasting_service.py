"""Prepare processed sales data and generate the initial Prophet forecast."""

from pathlib import Path
from typing import Any

import pandas as pd

from backend.models.forecasting.prophet_model import ProphetForecaster


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SALES_PATH = PROJECT_ROOT / "data" / "processed" / "sales" / "cleaned_sales.csv"
FORECAST_DIR = PROJECT_ROOT / "data" / "processed" / "forecast"
DAILY_SALES_PATH = FORECAST_DIR / "daily_sales.csv"
DAILY_PRODUCT_SALES_PATH = FORECAST_DIR / "daily_product_sales.csv"
FORECAST_PATH = FORECAST_DIR / "sales_forecast.csv"
FORECAST_HORIZON_DAYS = 30
VALIDATION_DAYS = 30


def load_processed_sales() -> pd.DataFrame:
    """Load the existing cleaned Sales dataset without changing it."""
    if not SALES_PATH.exists():
        raise FileNotFoundError(f"Processed sales dataset not found: {SALES_PATH}")

    sales = pd.read_csv(SALES_PATH)
    required_columns = {"transaction_id", "date", "product_id", "product_name", "quantity", "total_amount"}
    missing_columns = required_columns.difference(sales.columns)
    if missing_columns:
        raise ValueError(f"Sales dataset is missing required columns: {sorted(missing_columns)}")
    sales["date"] = pd.to_datetime(sales["date"], errors="coerce")
    sales["quantity"] = pd.to_numeric(sales["quantity"], errors="coerce")
    sales["total_amount"] = pd.to_numeric(sales["total_amount"], errors="coerce")
    sales = sales.dropna(subset=["date", "quantity", "total_amount"]).copy()
    return sales


def prepare_time_series(sales: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Create daily overall and product-level sales datasets with calendar signals."""
    daily_sales = (
        sales.groupby("date", as_index=False)
        .agg(
            sales_quantity=("quantity", "sum"),
            revenue=("total_amount", "sum"),
            transaction_count=("transaction_id", "nunique"),
        )
        .sort_values("date")
    )
    complete_dates = pd.date_range(daily_sales["date"].min(), daily_sales["date"].max(), freq="D")
    daily_sales = daily_sales.set_index("date").reindex(complete_dates, fill_value=0).rename_axis("date").reset_index()
    daily_sales["day_of_week"] = daily_sales["date"].dt.dayofweek
    daily_sales["month"] = daily_sales["date"].dt.month
    daily_sales["is_weekend"] = daily_sales["day_of_week"].isin([5, 6])

    daily_product_sales = (
        sales.groupby(["date", "product_id", "product_name"], as_index=False)
        .agg(
            sales_quantity=("quantity", "sum"),
            revenue=("total_amount", "sum"),
        )
        .sort_values(["date", "product_id"])
    )
    return daily_sales, daily_product_sales


def chronological_split(daily_sales: pd.DataFrame, validation_days: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Keep the latest dates as validation data and never shuffle observations."""
    if len(daily_sales) <= validation_days:
        raise ValueError("The time series must be longer than the validation window.")
    split_index = len(daily_sales) - validation_days
    return daily_sales.iloc[:split_index].copy(), daily_sales.iloc[split_index:].copy()


def _prophet_frame(data: pd.DataFrame, value_column: str) -> pd.DataFrame:
    """Convert a prepared daily metric to Prophet's ds/y schema."""
    return data[["date", value_column]].rename(columns={"date": "ds", value_column: "y"})


def _validation_mae(actual: pd.Series, predicted: pd.Series) -> float:
    """Calculate mean absolute error for a chronological holdout."""
    return float((actual.reset_index(drop=True) - predicted.reset_index(drop=True)).abs().mean())


def _forecast_metric(
    daily_sales: pd.DataFrame,
    value_column: str,
    validation_days: int,
    forecast_horizon: int,
) -> tuple[pd.DataFrame, float]:
    """Validate on the final historical window, then forecast after all history."""
    train, validation = chronological_split(daily_sales, validation_days)
    forecaster = ProphetForecaster()
    validation_forecast = forecaster.forecast(_prophet_frame(train, value_column), len(validation))
    validation_mae = _validation_mae(validation[value_column], validation_forecast["forecast"])

    future_forecast = forecaster.forecast(_prophet_frame(daily_sales, value_column), forecast_horizon)
    future_forecast["forecast"] = future_forecast["forecast"].clip(lower=0).round(2)
    future_forecast["metric"] = value_column
    return future_forecast.rename(columns={"ds": "date"})[["date", "metric", "forecast"]], validation_mae


def generate_forecast() -> dict[str, Any]:
    """Prepare data, validate Prophet chronologically, and save future forecasts."""
    sales = load_processed_sales()
    daily_sales, daily_product_sales = prepare_time_series(sales)
    revenue_forecast, revenue_mae = _forecast_metric(
        daily_sales, "revenue", VALIDATION_DAYS, FORECAST_HORIZON_DAYS
    )
    quantity_forecast, quantity_mae = _forecast_metric(
        daily_sales, "sales_quantity", VALIDATION_DAYS, FORECAST_HORIZON_DAYS
    )
    forecast = pd.concat([revenue_forecast, quantity_forecast], ignore_index=True)
    forecast["date"] = pd.to_datetime(forecast["date"]).dt.strftime("%Y-%m-%d")
    forecast = forecast.sort_values(["date", "metric"]).reset_index(drop=True)

    FORECAST_DIR.mkdir(parents=True, exist_ok=True)
    daily_sales.to_csv(DAILY_SALES_PATH, index=False)
    daily_product_sales.to_csv(DAILY_PRODUCT_SALES_PATH, index=False)
    forecast.to_csv(FORECAST_PATH, index=False)

    train, validation = chronological_split(daily_sales, VALIDATION_DAYS)
    return {
        "sales_rows": len(sales),
        "daily_rows": len(daily_sales),
        "product_daily_rows": len(daily_product_sales),
        "historical_start": daily_sales["date"].min().strftime("%Y-%m-%d"),
        "historical_end": daily_sales["date"].max().strftime("%Y-%m-%d"),
        "train_rows": len(train),
        "validation_rows": len(validation),
        "validation_start": validation["date"].min().strftime("%Y-%m-%d"),
        "validation_end": validation["date"].max().strftime("%Y-%m-%d"),
        "forecast_horizon_days": FORECAST_HORIZON_DAYS,
        "forecast_start": forecast["date"].min(),
        "forecast_end": forecast["date"].max(),
        "revenue_validation_mae": round(revenue_mae, 2),
        "quantity_validation_mae": round(quantity_mae, 2),
        "forecast_preview": forecast.head(6).to_dict(orient="records"),
        "output_paths": [DAILY_SALES_PATH, DAILY_PRODUCT_SALES_PATH, FORECAST_PATH],
    }


def main() -> None:
    """Run the forecasting job and print validation and output information."""
    result = generate_forecast()
    print(f"Processed sales rows: {result['sales_rows']:,}")
    print(f"Prepared daily rows: {result['daily_rows']:,}")
    print(f"Prepared product-day rows: {result['product_daily_rows']:,}")
    print(f"Historical range: {result['historical_start']} to {result['historical_end']}")
    print(
        f"Chronological split: {result['train_rows']:,} train rows, "
        f"{result['validation_rows']:,} validation rows "
        f"({result['validation_start']} to {result['validation_end']})"
    )
    print(f"Forecast horizon: {result['forecast_horizon_days']} days")
    print(f"Future forecast range: {result['forecast_start']} to {result['forecast_end']}")
    print(f"Revenue validation MAE: {result['revenue_validation_mae']:.2f}")
    print(f"Quantity validation MAE: {result['quantity_validation_mae']:.2f}")
    print("Forecast preview:")
    for row in result["forecast_preview"]:
        print(f"  {row['date']} | {row['metric']} | {row['forecast']:.2f}")
    for output_path in result["output_paths"]:
        print(f"Output: {output_path.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
