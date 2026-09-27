import pandas as pd
from prophet import Prophet


# -----------------------------------------
# LOAD CLEANED SALES DATA
# -----------------------------------------

sales_df = pd.read_csv(
    "data/clean_retail_sales.csv"
)

print("Sales data loaded successfully!")
print("Total rows:", len(sales_df))


# -----------------------------------------
# PREPARE DATE AND REVENUE
# -----------------------------------------

sales_df["InvoiceDate"] = pd.to_datetime(
    sales_df["InvoiceDate"],
    errors="coerce"
)

sales_df["Revenue"] = pd.to_numeric(
    sales_df["Revenue"],
    errors="coerce"
)

sales_df = sales_df.dropna(
    subset=["InvoiceDate", "Revenue"]
)

# -----------------------------------------
# BUILD DAILY REVENUE
# -----------------------------------------

daily_revenue = (
    sales_df
    .groupby(
        sales_df["InvoiceDate"].dt.date
    )["Revenue"]
    .sum()
    .reset_index()
)

daily_revenue.columns = [
    "date",
    "revenue"
]

daily_revenue["date"] = pd.to_datetime(
    daily_revenue["date"]
)


# -----------------------------------------
# FILL MISSING CALENDAR DAYS WITH ZERO
# -----------------------------------------

full_date_range = pd.date_range(
    start=daily_revenue["date"].min(),
    end=daily_revenue["date"].max(),
    freq="D"
)

daily_revenue = (
    daily_revenue
    .set_index("date")
    .reindex(full_date_range)
    .fillna(0)
    .rename_axis("date")
    .reset_index()
)


print("\nDaily Revenue after filling missing dates:")

print(
    daily_revenue.head(10)
)

print(
    "\nTotal calendar days:",
    len(daily_revenue)
)

print(
    "Days with zero revenue:",
    (daily_revenue["revenue"] == 0).sum()
)

daily_revenue.columns = [
    "date",
    "revenue"
]

daily_revenue["date"] = pd.to_datetime(
    daily_revenue["date"]
)


# -----------------------------------------
# DISPLAY DAILY REVENUE
# -----------------------------------------

print("\nDaily Revenue:")
print(
    daily_revenue.head(10)
)

print(
    "\nTotal days with recorded sales:",
    len(daily_revenue)
)


# -----------------------------------------
# PREPARE DATA FOR PROPHET
# -----------------------------------------

prophet_df = daily_revenue.rename(
    columns={
        "date": "ds",
        "revenue": "y"
    }
)

print("\nProphet Input:")
print(
    prophet_df.head()
)


# -----------------------------------------
# BUILD PROPHET MODEL
# -----------------------------------------

model = Prophet()

model.fit(
    prophet_df
)

print(
    "\nProphet model trained successfully!"
)


# -----------------------------------------
# CREATE FUTURE DATES
# -----------------------------------------

future = model.make_future_dataframe(
    periods=30
)


# -----------------------------------------
# GENERATE FORECAST
# -----------------------------------------

forecast = model.predict(
    future
)


# -----------------------------------------
# DISPLAY FORECAST
# -----------------------------------------

forecast_output = forecast[
    [
        "ds",
        "yhat",
        "yhat_lower",
        "yhat_upper"
    ]
].tail(30)

print(
    "\nNext 30 Days Revenue Forecast:"
)

print(
    forecast_output.to_string(
        index=False
    )
)


# -----------------------------------------
# SAVE FORECAST
# -----------------------------------------

forecast_output.to_csv(
    "data/revenue_forecast.csv",
    index=False
)

print(
    "\nForecast saved successfully!"
)

print(
    "File: data/revenue_forecast.csv"
)


# -----------------------------------------
# CREATE FORECAST PLOT
# -----------------------------------------

fig = model.plot(
    forecast
)

fig.savefig(
    "data/revenue_forecast.png"
)

print(
    "Forecast graph saved successfully!"
)


# -----------------------------------------
# CREATE FORECAST COMPONENTS
# -----------------------------------------

fig2 = model.plot_components(
    forecast
)

fig2.savefig(
    "data/forecast_components.png"
)

print(
    "Forecast components saved successfully!"
)