"""M2: segment summary, 30-day revenue forecast and the Excel business report -> outputs/
Run after: segmentation.py, forecasting_models.py (and optionally the M3 scripts for the extra sheets)."""
import pandas as pd
from openpyxl.styles import Font
from forecasting_models import daily_revenue, fit_best, recursive_forecast
from common import OUT, load_json, save_json


def main():
    daily = daily_revenue()
    results, best, model, info = fit_best(daily)
    best_metrics = next(r for r in results if r["model"] == best)
    fc = recursive_forecast(model, daily, 30, band=1.96 * best_metrics["rmse"])     # approx. 95% band from the test RMSE
    forecast = {"period": "Next 30 Days", "predicted_revenue": round(sum(d["revenue"] for d in fc), 2), "model_used": best,
                "metrics": {k: round(best_metrics[k], 3) for k in ("mae", "rmse", "mape", "r2")},
                "evaluation": info,
                "note": "daily lower/upper = prediction +/- 1.96 x test RMSE (approximate band, not a model-based interval)",
                "history": [{"date": d.strftime("%Y-%m-%d"), "revenue": round(r, 2)} for d, r in zip(daily["date"].tail(60), daily["revenue"].tail(60))],
                "daily": fc}
    save_json("forecast.json", forecast)
    segments = pd.DataFrame(load_json("segments.json", []))

    with pd.ExcelWriter(OUT / "business_report.xlsx", engine="openpyxl") as xw:
        segments.to_excel(xw, sheet_name="Customer Segments", index=False)
        pd.DataFrame([{"period": forecast["period"], "predicted_revenue": forecast["predicted_revenue"], "model_used": best}]).to_excel(xw, sheet_name="Sales Forecast", index=False)
        pd.DataFrame(fc).rename(columns={"revenue": "forecast_revenue"}).to_excel(xw, sheet_name="Sales Forecast", index=False, startrow=4)
        pd.DataFrame(results).round(3).to_excel(xw, sheet_name="Model Comparison", index=False)
        for sheet, f, n in (("Top Churn Risk", "churn_predictions.csv", 100), ("Anomaly Alerts", "anomaly_alerts.csv", 200)):
            if (OUT / f).exists():
                pd.read_csv(OUT / f).head(n).to_excel(xw, sheet_name=sheet, index=False)
        for ws in xw.book.worksheets:                       # readable column widths + bold header
            for col in ws.columns:
                ws.column_dimensions[col[0].column_letter].width = min(60, max(12, max(len(str(c.value or "")) for c in col[:50]) + 2))
            for c in ws[1]:
                c.font = Font(bold=True)
    print(f"Forecast {forecast['predicted_revenue']:,.0f} next 30 days ({best}); report saved: outputs/business_report.xlsx")


if __name__ == "__main__":
    main()
