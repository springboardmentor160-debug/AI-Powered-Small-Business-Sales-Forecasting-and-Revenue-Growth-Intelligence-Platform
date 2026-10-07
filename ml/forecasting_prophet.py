"""
Sales Forecasting -- MarketMind AI
Milestone 2, Day 5-6: Forecasting Setup (Prophet)

Aggregates sales_data_prepped.csv to one daily total demand series
(across all stores/products) and runs a first-pass Prophet forecast.

    python forecasting_prophet.py

Outputs:
    - forecast_plot.png -- historical + forecasted demand
    - forecast_components.png -- trend/weekly/yearly seasonality breakdown
    - forecast_output.csv -- predicted values for the next 90 days
"""

import pandas as pd
from prophet import Prophet
import matplotlib.pyplot as plt

# ---------------------------------------------------------------------------
# 1. Load and aggregate to a single daily time series
# ---------------------------------------------------------------------------
# sales_data_prepped.csv is store/product/day level (76,000 rows). Prophet
# needs one time series, so this aggregates to total daily Demand across
# all stores and products -- the most basic, sensible first forecast.
# Per-store or per-product forecasting is a natural next refinement, not
# needed for this milestone's "get a basic forecast out" bar.
df = pd.read_csv("../datasets/processed/sales_data_prepped.csv")
df["Date"] = pd.to_datetime(df["Date"])

daily = df.groupby("Date")["Demand"].sum().reset_index()
daily.columns = ["ds", "y"]  # Prophet requires these exact column names

print(f"Daily series: {len(daily)} days, {daily['ds'].min()} to {daily['ds'].max()}")
print(daily.head())

# ---------------------------------------------------------------------------
# 2. Fit Prophet
# ---------------------------------------------------------------------------
model = Prophet()
model.fit(daily)

# ---------------------------------------------------------------------------
# 3. Forecast 90 days beyond the historical data
# ---------------------------------------------------------------------------
future = model.make_future_dataframe(periods=90)
forecast = model.predict(future)

print("\nForecast tail (last 5 predicted rows):")
print(forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]].tail())

# ---------------------------------------------------------------------------
# 4. Save plots
# ---------------------------------------------------------------------------
fig1 = model.plot(forecast)
plt.title("Daily Demand -- Historical + 90-Day Forecast")
fig1.savefig("forecast_plot.png")

fig2 = model.plot_components(forecast)
fig2.savefig("forecast_components.png")

print("\nSaved forecast_plot.png and forecast_components.png")

# ---------------------------------------------------------------------------
# 5. Save forecast output
# ---------------------------------------------------------------------------
forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]].to_csv(
    "forecast_output.csv", index=False
)
print("Saved forecast_output.csv")