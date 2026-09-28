"""Reporting integration for generated segmentation and forecasting results."""

from pathlib import Path
from typing import Any

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
SEGMENTS_PATH = PROCESSED_DIR / "segments" / "customer_segments.csv"
FORECAST_PATH = PROCESSED_DIR / "forecast" / "sales_forecast.csv"
MODEL_COMPARISON_PATH = PROCESSED_DIR / "forecast" / "model_comparison.csv"
REPORT_DIR = PROCESSED_DIR / "reports"
REPORT_PATH = REPORT_DIR / "marketmind_day9_10_report.xlsx"


def _load_results() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Load only generated segmentation and forecasting outputs."""
    paths = (SEGMENTS_PATH, FORECAST_PATH, MODEL_COMPARISON_PATH)
    missing = [path for path in paths if not path.exists()]
    if missing:
        raise FileNotFoundError(f"Generated reporting input not found: {missing}")
    segments = pd.read_csv(SEGMENTS_PATH)
    forecast = pd.read_csv(FORECAST_PATH)
    comparison = pd.read_csv(MODEL_COMPARISON_PATH)
    return segments, forecast, comparison


def _segment_summary(segments: pd.DataFrame) -> pd.DataFrame:
    """Summarize actual customer counts and behavior by named segment."""
    return (
        segments.groupby("segment_name", as_index=False)
        .agg(
            customer_count=("customer_id", "nunique"),
            average_purchase_frequency=("purchase_frequency", "mean"),
            average_purchase_value=("purchase_value", "mean"),
            average_customer_activity=("customer_activity", "mean"),
        )
        .sort_values(["customer_count", "segment_name"], ascending=[False, True])
        .round(2)
    )


def _segment_statistics(segments: pd.DataFrame) -> pd.DataFrame:
    """Summarize actual hierarchical cluster behavior."""
    return (
        segments.groupby(["hierarchical_cluster", "segment_name"], as_index=False)
        .agg(
            customer_count=("customer_id", "nunique"),
            mean_purchase_frequency=("purchase_frequency", "mean"),
            mean_purchase_value=("purchase_value", "mean"),
            mean_customer_activity=("customer_activity", "mean"),
        )
        .sort_values("hierarchical_cluster")
        .round(2)
    )


def _forecast_summary(forecast: pd.DataFrame, comparison: pd.DataFrame) -> pd.DataFrame:
    """Summarize the generated revenue forecast and selected model."""
    revenue_forecast = forecast[forecast["metric"] == "revenue"].copy()
    selected_comparison = comparison[
        (comparison["metric"] == "revenue") & (comparison["selected"])
    ]
    selected_model = str(selected_comparison.iloc[0]["model"])
    return pd.DataFrame(
        [
            {
                "metric": "revenue",
                "selected_model": selected_model,
                "forecast_start": revenue_forecast["date"].min(),
                "forecast_end": revenue_forecast["date"].max(),
                "forecast_days": len(revenue_forecast),
                "average_daily_forecast": round(float(revenue_forecast["forecast"].mean()), 2),
                "total_forecast_value": round(float(revenue_forecast["forecast"].sum()), 2),
            }
        ]
    )


def _business_interpretation(
    segment_summary: pd.DataFrame,
    forecast_summary: pd.DataFrame,
    comparison: pd.DataFrame,
) -> pd.DataFrame:
    """Create concise interpretations from the actual generated summaries."""
    largest_segment = segment_summary.iloc[0]
    high_value_segment = segment_summary.loc[
        segment_summary["average_purchase_value"].idxmax()
    ]
    selected_model = forecast_summary.iloc[0]["selected_model"]
    revenue_results = comparison[comparison["metric"] == "revenue"].sort_values("rmse")
    best_rmse = float(revenue_results.iloc[0]["rmse"])
    interpretation = [
        f"The largest customer segment is {largest_segment['segment_name']} with {int(largest_segment['customer_count'])} customers.",
        f"{high_value_segment['segment_name']} has the highest average purchase value at {high_value_segment['average_purchase_value']:.2f}.",
        f"The selected revenue forecast model is {selected_model}, with validation RMSE {best_rmse:.2f}.",
        f"The generated revenue forecast covers {forecast_summary.iloc[0]['forecast_start']} to {forecast_summary.iloc[0]['forecast_end']}.",
    ]
    return pd.DataFrame({"business_interpretation": interpretation})


def get_segments_report() -> dict[str, Any]:
    """Return actual segmentation summaries for the protected API."""
    segments, _, _ = _load_results()
    summary = _segment_summary(segments)
    statistics = _segment_statistics(segments)
    return {
        "customers_processed": int(segments["customer_id"].nunique()),
        "segments": summary.to_dict(orient="records"),
        "cluster_statistics": statistics.to_dict(orient="records"),
    }


def get_revenue_forecast_report() -> dict[str, Any]:
    """Return actual revenue forecasts and revenue model comparison results."""
    _, forecast, comparison = _load_results()
    revenue_forecast = forecast[forecast["metric"] == "revenue"].copy()
    revenue_comparison = comparison[comparison["metric"] == "revenue"].copy()
    selected_model = str(revenue_comparison.loc[revenue_comparison["selected"], "model"].iloc[0])
    return {
        "metric": "revenue",
        "selected_model": selected_model,
        "forecast_start": str(revenue_forecast["date"].min()),
        "forecast_end": str(revenue_forecast["date"].max()),
        "forecast": revenue_forecast.to_dict(orient="records"),
        "model_comparison": revenue_comparison.to_dict(orient="records"),
    }


def generate_excel_report() -> Path:
    """Write the factual Day 9-10 workbook from generated CSV outputs."""
    segments, forecast, comparison = _load_results()
    segment_summary = _segment_summary(segments)
    segment_statistics = _segment_statistics(segments)
    forecast_summary = _forecast_summary(forecast, comparison)
    revenue_forecast = forecast[forecast["metric"] == "revenue"].copy()
    model_comparison = comparison.copy()
    interpretation = _business_interpretation(segment_summary, forecast_summary, comparison)

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(REPORT_PATH, engine="openpyxl") as writer:
        segment_summary.to_excel(writer, sheet_name="Segment Summary", index=False)
        segment_statistics.to_excel(writer, sheet_name="Segment Statistics", index=False)
        forecast_summary.to_excel(writer, sheet_name="Forecast Summary", index=False)
        revenue_forecast.to_excel(writer, sheet_name="Revenue Forecast", index=False)
        model_comparison.to_excel(writer, sheet_name="Model Comparison", index=False)
        interpretation.to_excel(writer, sheet_name="Business Interpretation", index=False)
    return REPORT_PATH


def main() -> None:
    """Generate the Excel report and print actual report dimensions and location."""
    report_path = generate_excel_report()
    segments_report = get_segments_report()
    forecast_report = get_revenue_forecast_report()
    print(f"Customers reported: {segments_report['customers_processed']:,}")
    print(f"Segments reported: {len(segments_report['segments'])}")
    print(f"Revenue forecast rows: {len(forecast_report['forecast'])}")
    print(f"Selected revenue model: {forecast_report['selected_model']}")
    print(f"Excel report: {report_path.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
