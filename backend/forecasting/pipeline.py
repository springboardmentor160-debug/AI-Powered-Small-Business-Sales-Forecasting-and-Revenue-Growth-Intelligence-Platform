import os
import pandas as pd
import numpy as np
from typing import Dict, Any, Tuple, List
from prophet import Prophet
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for server environment
import matplotlib.pyplot as plt


RAW_CSV_PATH = os.path.join("data", "processed", "clean_sales_data.csv")
DAILY_REVENUE_CSV_PATH = os.path.join("data", "processed", "daily_revenue.csv")
REPORTS_DIR = os.path.join("reports")
FORECAST_PLOT_PATH = os.path.join(REPORTS_DIR, "forecast_chart.png")
COMPONENTS_PLOT_PATH = os.path.join(REPORTS_DIR, "forecast_components.png")


def prepare_daily_revenue(sales_df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    1. Group sales by date to compute daily revenue (total_amount = quantity * unit_price).
    2. Missing Date Check: Identify dates between min and max order dates with no recorded sales.
    """
    df = sales_df.copy()
    df['order_date'] = pd.to_datetime(df['order_date'])

    if 'total_amount' not in df.columns:
        df['total_amount'] = df['quantity'] * df['unit_price']

    # Group by date
    daily_df = df.groupby('order_date')['total_amount'].sum().reset_index()
    daily_df.columns = ['date', 'revenue']
    daily_df['date'] = pd.to_datetime(daily_df['date'])
    daily_df = daily_df.sort_values('date').reset_index(drop=True)

    # Missing date check
    min_date = daily_df['date'].min()
    max_date = daily_df['date'].max()
    full_date_range = pd.date_range(start=min_date, end=max_date, freq='D')
    
    existing_dates = set(daily_df['date'])
    missing_dates = [d.strftime('%Y-%m-%d') for d in full_date_range if d not in existing_dates]

    missing_info = {
        "min_date": min_date.strftime('%Y-%m-%d'),
        "max_date": max_date.strftime('%Y-%m-%d'),
        "total_days_in_range": len(full_date_range),
        "recorded_days": len(daily_df),
        "missing_dates_count": len(missing_dates),
        "missing_dates": missing_dates
    }

    return daily_df, missing_info


def run_forecasting_pipeline(
    sales_csv_path: str = RAW_CSV_PATH,
    daily_revenue_csv_path: str = DAILY_REVENUE_CSV_PATH,
    forecast_periods: int = 30
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Full Sales Forecasting Pipeline (Days 5–6):
    1. Prepare daily revenue time-series
    2. Conduct missing date check
    3. Format data into Prophet ds/y format
    4. Fit Prophet model and forecast 30 future days
    5. Generate and save forecast visualization charts
    6. Return forecast dataframe and summary payload
    """
    if not os.path.exists(sales_csv_path):
        raise FileNotFoundError(f"Sales dataset not found at {sales_csv_path}")

    sales_df = pd.read_csv(sales_csv_path)
    daily_df, missing_info = prepare_daily_revenue(sales_df)

    # Save daily_revenue.csv
    os.makedirs(os.path.dirname(daily_revenue_csv_path), exist_ok=True)
    daily_export = daily_df.copy()
    daily_export['date'] = daily_export['date'].dt.strftime('%Y-%m-%d')
    daily_export.to_csv(daily_revenue_csv_path, index=False)

    # Format for Prophet (requires columns: 'ds' and 'y')
    prophet_df = daily_df.rename(columns={'date': 'ds', 'revenue': 'y'})

    # Fit Prophet model
    model = Prophet(
        yearly_seasonality=False,  # Small sample data check
        weekly_seasonality=False,
        daily_seasonality=False,
        interval_width=0.95
    )
    model.fit(prophet_df)

    # Make future dataframe for 30-day forecast
    future = model.make_future_dataframe(periods=forecast_periods)
    forecast = model.predict(future)

    # Extract required fields: ds, yhat, yhat_lower, yhat_upper
    forecast_results = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].copy()

    # Generate and save forecast plot
    os.makedirs(REPORTS_DIR, exist_ok=True)
    
    fig1 = model.plot(forecast)
    plt.title("MarketMind AI — 30-Day Revenue Forecast (Prophet)")
    plt.xlabel("Date")
    plt.ylabel("Revenue ($)")
    plt.tight_layout()
    fig1.savefig(FORECAST_PLOT_PATH)
    plt.close(fig1)

    # Generate and save forecast components plot
    try:
        fig2 = model.plot_components(forecast)
        fig2.tight_layout()
        fig2.savefig(COMPONENTS_PLOT_PATH)
        plt.close(fig2)
    except Exception as e:
        # Fallback if component plot fails due to simple model
        print(f"Plot components notice: {e}")

    # Build summary data payload
    recent_history = [
        {"date": row['date'].strftime('%Y-%m-%d'), "revenue": round(float(row['revenue']), 2)}
        for _, row in daily_df.iterrows()
    ]

    forecast_items = []
    # Filter to only future predictions (or all)
    for _, row in forecast_results.iterrows():
        forecast_items.append({
            "ds": row['ds'].strftime('%Y-%m-%d'),
            "yhat": round(float(row['yhat']), 2),
            "yhat_lower": round(float(row['yhat_lower']), 2),
            "yhat_upper": round(float(row['yhat_upper']), 2)
        })

    summary_payload = {
        "historical_period": {
            "start_date": missing_info["min_date"],
            "end_date": missing_info["max_date"],
            "recorded_days": missing_info["recorded_days"]
        },
        "missing_dates_summary": {
            "count": missing_info["missing_dates_count"],
            "dates": missing_info["missing_dates"]
        },
        "forecast_horizon": forecast_periods,
        "recent_history": recent_history,
        "forecast": forecast_items,
        "future_only_forecast": forecast_items[-forecast_periods:],
        "plots": {
            "forecast_chart": FORECAST_PLOT_PATH,
            "components_chart": COMPONENTS_PLOT_PATH
        },
        "limitations": (
            "The sample dataset is small (8 orders across 6 calendar days). "
            "Prophet forecast uncertainty bounds are appropriately wide and seasonal patterns cannot be fully inferred."
        )
    }

    return forecast_results, summary_payload
