"""Prepare processed sales data and generate the initial Prophet forecast."""

from pathlib import Path
from typing import Any

import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error

from backend.models.forecasting.feature_engineering import TimeSeriesFeatureBuilder
from backend.models.forecasting.prophet_model import ProphetForecaster
from backend.models.forecasting.tree_models import RandomForestForecaster, XGBoostForecaster


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SALES_PATH = PROJECT_ROOT / "data" / "processed" / "sales" / "cleaned_sales.csv"
FORECAST_DIR = PROJECT_ROOT / "data" / "processed" / "forecast"
DAILY_SALES_PATH = FORECAST_DIR / "daily_sales.csv"
DAILY_PRODUCT_SALES_PATH = FORECAST_DIR / "daily_product_sales.csv"
FORECAST_PATH = FORECAST_DIR / "sales_forecast.csv"
FEATURES_PATH = FORECAST_DIR / "feature_engineered_sales.csv"
MODEL_COMPARISON_PATH = FORECAST_DIR / "model_comparison.csv"
MODEL_VALIDATION_PATH = FORECAST_DIR / "model_validation_predictions.csv"
ALL_MODEL_FORECASTS_PATH = FORECAST_DIR / "model_forecasts.csv"
FORECAST_HORIZON_DAYS = 30
VALIDATION_DAYS = 30
TARGET_COLUMNS = ["revenue", "sales_quantity"]
MODEL_NAMES = ["Prophet", "XGBoost", "Random Forest"]


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


def _calculate_metrics(actual: pd.Series, predicted: pd.Series) -> tuple[float, float]:
    """Return MAE and RMSE for one chronological validation window."""
    actual_values = actual.to_numpy()
    predicted_values = predicted.to_numpy()
    return (
        float(mean_absolute_error(actual_values, predicted_values)),
        float(mean_squared_error(actual_values, predicted_values) ** 0.5),
    )


def _recursive_tree_forecast(
    model: Any,
    daily_sales: pd.DataFrame,
    target_column: str,
    feature_builder: TimeSeriesFeatureBuilder,
    periods: int,
) -> pd.DataFrame:
    """Generate future tree predictions using prior actuals and predictions as lags."""
    history = daily_sales[target_column].astype(float).tolist()
    current_date = pd.Timestamp(daily_sales["date"].max())
    rows = []
    for day_offset in range(1, periods + 1):
        forecast_date = current_date + pd.to_timedelta(day_offset, unit="D")
        feature_row = feature_builder.build_future_row(history, forecast_date)
        prediction = float(model.predict(pd.DataFrame([feature_row])[feature_builder.feature_columns])[0])
        prediction = max(0.0, prediction)
        history.append(prediction)
        rows.append({"date": forecast_date, "forecast": round(prediction, 2)})
    return pd.DataFrame(rows)


def _build_feature_export(
    daily_sales: pd.DataFrame,
    feature_builder: TimeSeriesFeatureBuilder,
) -> pd.DataFrame:
    """Save both target-specific feature sets in one prepared-data file."""
    feature_frames = []
    for target_column in TARGET_COLUMNS:
        frame = feature_builder.build(daily_sales, target_column)
        frame = frame.rename(
            columns={
                target_column: f"{target_column}_actual",
                **{column: f"{target_column}_{column}" for column in feature_builder.feature_columns},
            }
        )
        feature_frames.append(frame.set_index("date"))
    return pd.concat(feature_frames, axis=1).reset_index()


def _evaluate_all_models(
    daily_sales: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict[str, str], pd.DataFrame]:
    """Evaluate Prophet, XGBoost, and Random Forest without shuffling dates."""
    feature_builder = TimeSeriesFeatureBuilder()
    comparison_rows = []
    validation_rows = []
    future_rows = []

    for target_column in TARGET_COLUMNS:
        train, validation = chronological_split(daily_sales, VALIDATION_DAYS)

        prophet = ProphetForecaster()
        prophet_validation = prophet.forecast(_prophet_frame(train, target_column), len(validation))
        prophet_future = prophet.forecast(_prophet_frame(daily_sales, target_column), FORECAST_HORIZON_DAYS)
        prophet_validation_predictions = prophet_validation["forecast"].clip(lower=0)
        prophet_mae, prophet_rmse = _calculate_metrics(validation[target_column], prophet_validation_predictions)
        comparison_rows.append({"model": "Prophet", "metric": target_column, "mae": prophet_mae, "rmse": prophet_rmse})
        validation_rows.extend(
            {
                "date": date,
                "metric": target_column,
                "model": "Prophet",
                "actual": actual,
                "prediction": prediction,
            }
            for date, actual, prediction in zip(
                validation["date"], validation[target_column], prophet_validation_predictions
            )
        )
        future_rows.extend(
            {"date": date, "metric": target_column, "model": "Prophet", "forecast": max(0.0, round(float(value), 2))}
            for date, value in zip(prophet_future["ds"], prophet_future["forecast"])
        )

        feature_data = feature_builder.build(daily_sales, target_column)
        feature_train = feature_data.iloc[:-VALIDATION_DAYS].copy()
        feature_validation = feature_data.iloc[-VALIDATION_DAYS:].copy()
        for model_name, model_wrapper in (
            ("XGBoost", XGBoostForecaster()),
            ("Random Forest", RandomForestForecaster()),
        ):
            validation_predictions = model_wrapper.fit_predict(
                feature_train,
                feature_validation,
                feature_builder.feature_columns,
                target_column,
            ).clip(lower=0)
            model_mae, model_rmse = _calculate_metrics(
                feature_validation[target_column], validation_predictions
            )
            comparison_rows.append(
                {"model": model_name, "metric": target_column, "mae": model_mae, "rmse": model_rmse}
            )
            validation_rows.extend(
                {
                    "date": date,
                    "metric": target_column,
                    "model": model_name,
                    "actual": actual,
                    "prediction": prediction,
                }
                for date, actual, prediction in zip(
                    feature_validation["date"],
                    feature_validation[target_column],
                    validation_predictions,
                )
            )
            full_model = model_wrapper.fit(
                feature_data,
                feature_builder.feature_columns,
                target_column,
            )
            tree_future = _recursive_tree_forecast(
                full_model,
                daily_sales,
                target_column,
                feature_builder,
                FORECAST_HORIZON_DAYS,
            )
            future_rows.extend(
                {
                    "date": row["date"],
                    "metric": target_column,
                    "model": model_name,
                    "forecast": row["forecast"],
                }
                for _, row in tree_future.iterrows()
            )

    comparison = pd.DataFrame(comparison_rows)
    comparison["mae"] = comparison["mae"].round(2)
    comparison["rmse"] = comparison["rmse"].round(2)
    selected_models = {}
    for target_column in TARGET_COLUMNS:
        target_results = comparison[comparison["metric"] == target_column].sort_values(
            ["rmse", "mae", "model"]
        )
        selected_models[target_column] = str(target_results.iloc[0]["model"])
    comparison["selected"] = comparison.apply(
        lambda row: selected_models[row["metric"]] == row["model"], axis=1
    )
    all_forecasts = pd.DataFrame(future_rows).sort_values(["date", "metric", "model"]).reset_index(drop=True)
    selected_forecasts = all_forecasts[
        all_forecasts.apply(lambda row: selected_models[row["metric"]] == row["model"], axis=1)
    ].copy()
    selected_forecasts = selected_forecasts.sort_values(["date", "metric"]).reset_index(drop=True)
    validation_predictions = pd.DataFrame(validation_rows).sort_values(
        ["date", "metric", "model"]
    ).reset_index(drop=True)
    return comparison, validation_predictions, all_forecasts, selected_models, selected_forecasts


def generate_forecast() -> dict[str, Any]:
    """Prepare data, compare models chronologically, and save selected forecasts."""
    sales = load_processed_sales()
    daily_sales, daily_product_sales = prepare_time_series(sales)
    train, validation = chronological_split(daily_sales, VALIDATION_DAYS)
    feature_builder = TimeSeriesFeatureBuilder()
    feature_export = _build_feature_export(daily_sales, feature_builder)
    comparison, validation_predictions, all_forecasts, selected_models, selected_forecasts = _evaluate_all_models(
        daily_sales
    )
    forecast = selected_forecasts.copy()
    historical_start = daily_sales["date"].min().strftime("%Y-%m-%d")
    historical_end = daily_sales["date"].max().strftime("%Y-%m-%d")
    forecast_start = forecast["date"].min().strftime("%Y-%m-%d")
    forecast_end = forecast["date"].max().strftime("%Y-%m-%d")
    for frame in (feature_export, daily_sales, daily_product_sales, comparison, validation_predictions, all_forecasts, forecast):
        if "date" in frame.columns:
            frame["date"] = pd.to_datetime(frame["date"]).dt.strftime("%Y-%m-%d")

    FORECAST_DIR.mkdir(parents=True, exist_ok=True)
    daily_sales.to_csv(DAILY_SALES_PATH, index=False)
    daily_product_sales.to_csv(DAILY_PRODUCT_SALES_PATH, index=False)
    feature_export.to_csv(FEATURES_PATH, index=False)
    comparison.to_csv(MODEL_COMPARISON_PATH, index=False)
    validation_predictions.to_csv(MODEL_VALIDATION_PATH, index=False)
    all_forecasts.to_csv(ALL_MODEL_FORECASTS_PATH, index=False)
    forecast.to_csv(FORECAST_PATH, index=False)

    selected_rows = comparison[comparison["selected"]].to_dict(orient="records")
    return {
        "sales_rows": len(sales),
        "daily_rows": len(daily_sales),
        "product_daily_rows": len(daily_product_sales),
        "historical_start": historical_start,
        "historical_end": historical_end,
        "train_rows": len(train),
        "validation_rows": len(validation),
        "validation_start": validation["date"].min().strftime("%Y-%m-%d"),
        "validation_end": validation["date"].max().strftime("%Y-%m-%d"),
        "forecast_horizon_days": FORECAST_HORIZON_DAYS,
        "forecast_start": forecast_start,
        "forecast_end": forecast_end,
        "selected_models": selected_models,
        "model_comparison": comparison.to_dict(orient="records"),
        "selected_rows": selected_rows,
        "forecast_preview": forecast.head(6).to_dict(orient="records"),
        "output_paths": [
            DAILY_SALES_PATH,
            DAILY_PRODUCT_SALES_PATH,
            FEATURES_PATH,
            MODEL_COMPARISON_PATH,
            MODEL_VALIDATION_PATH,
            ALL_MODEL_FORECASTS_PATH,
            FORECAST_PATH,
        ],
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
    print("Model comparison (actual chronological validation):")
    for row in result["model_comparison"]:
        print(
            f"  {row['metric']} | {row['model']} | "
            f"MAE {row['mae']:.2f} | RMSE {row['rmse']:.2f} | selected={row['selected']}"
        )
    print(f"Selected models: {result['selected_models']}")
    print("Forecast preview:")
    for row in result["forecast_preview"]:
        print(f"  {row['date']} | {row['metric']} | {row['forecast']:.2f}")
    for output_path in result["output_paths"]:
        print(f"Output: {output_path.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
