import pandas as pd


# -----------------------------------------
# LOAD RESULTS
# -----------------------------------------

segments = pd.read_csv(
    "data/customer_segmentation_output.csv"
)

forecast = pd.read_csv(
    "data/revenue_forecast.csv"
)

model_comparison = pd.read_csv(
    "data/forecast_model_comparison.csv"
)


# -----------------------------------------
# CUSTOMER SEGMENT SUMMARY
# -----------------------------------------

segment_summary = (
    segments
    .groupby("segment")
    .agg(
        customer_count=("CustomerID", "count"),
        avg_purchase_frequency=(
            "purchase_frequency",
            "mean"
        ),
        avg_purchase_value=(
            "purchase_value",
            "mean"
        ),
        avg_activity_days=(
            "customer_activity_days",
            "mean"
        )
    )
    .round(2)
    .reset_index()
)


# -----------------------------------------
# FORECAST SUMMARY
# -----------------------------------------

forecast["ds"] = pd.to_datetime(
    forecast["ds"]
)

forecast_summary = forecast[
    [
        "ds",
        "yhat",
        "yhat_lower",
        "yhat_upper"
    ]
].copy()

forecast_summary.columns = [
    "Date",
    "Predicted Revenue",
    "Lower Bound",
    "Upper Bound"
]

forecast_summary[
    "Predicted Revenue"
] = forecast_summary[
    "Predicted Revenue"
].round(2)

forecast_summary[
    "Lower Bound"
] = forecast_summary[
    "Lower Bound"
].round(2)

forecast_summary[
    "Upper Bound"
] = forecast_summary[
    "Upper Bound"
].round(2)


# -----------------------------------------
# MODEL COMPARISON
# -----------------------------------------

model_comparison = model_comparison.round(2)


# -----------------------------------------
# CREATE EXCEL REPORT
# -----------------------------------------

output_file = "data/business_report.xlsx"

with pd.ExcelWriter(
    output_file,
    engine="openpyxl"
) as writer:

    segment_summary.to_excel(
        writer,
        sheet_name="Customer Segments",
        index=False
    )

    forecast_summary.to_excel(
        writer,
        sheet_name="Sales Forecast",
        index=False
    )

    model_comparison.to_excel(
        writer,
        sheet_name="Model Comparison",
        index=False
    )


print(
    "Business report created successfully!"
)

print(
    f"File: {output_file}"
)

print(
    "\nSheets created:"
)

print("1. Customer Segments")
print("2. Sales Forecast")
print("3. Model Comparison")