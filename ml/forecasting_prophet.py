"""M2: Prophet forecast on daily revenue, evaluated on the SAME time-based test window as forecasting_models.py.
Skips gracefully when prophet is not installed (pip install prophet)."""
import numpy as np
import pandas as pd
from common import OUT, save_json
from forecasting_models import daily_revenue, evaluate, test_window


def main():
    try:
        from prophet import Prophet
    except ImportError:
        print("prophet not installed - skipping (pip install prophet). The model comparison will omit it.")
        return
    daily, info = daily_revenue(return_info=True)
    print(f"Daily series: {info['days']} days, {info['missing_days_filled']} missing days filled")
    df = daily.rename(columns={"date": "ds", "revenue": "y"})
    test_start, n_test = test_window(daily)
    train, test = df[df["ds"] < test_start], df[df["ds"] >= test_start]
    m = Prophet(yearly_seasonality=True, weekly_seasonality=True).fit(train)
    pred = m.predict(test[["ds"]])["yhat"].values
    metrics = {**evaluate("Prophet", test["y"], pred), "test_start": str(test_start.date()), "test_days": int(n_test)}
    save_json("prophet_metrics.json", metrics)
    full = Prophet(yearly_seasonality=True, weekly_seasonality=True).fit(df)
    fc = full.predict(full.make_future_dataframe(periods=30))
    fc[["ds", "yhat", "yhat_lower", "yhat_upper"]].tail(30).to_csv(OUT / "prophet_forecast.csv", index=False)
    full.plot(fc).savefig(OUT / "revenue_forecast.png")
    full.plot_components(fc).savefig(OUT / "forecast_components.png")
    print(metrics)


if __name__ == "__main__":
    main()
