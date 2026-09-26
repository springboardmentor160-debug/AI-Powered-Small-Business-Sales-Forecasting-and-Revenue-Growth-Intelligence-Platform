import React, { useEffect, useState } from "react";
import { getForecastingSummary, downloadBusinessReport } from "../api";

export default function SalesForecast() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [downloading, setDownloading] = useState(false);
  const [error, setError] = useState(null);
  const [viewMode, setViewMode] = useState("table"); // 'table', 'models', or 'chart'

  useEffect(() => {
    async function fetchData() {
      try {
        setLoading(true);
        const res = await getForecastingSummary();
        setData(res);
      } catch (err) {
        setError(err.message || "Failed to load sales forecast data.");
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  const handleDownloadReport = async () => {
    try {
      setDownloading(true);
      await downloadBusinessReport();
    } catch (err) {
      alert("Failed to download business report: " + err.message);
    } finally {
      setDownloading(false);
    }
  };

  if (loading) {
    return (
      <div className="bg-white rounded-xl shadow-sm p-6 border border-slate-200 animate-pulse mb-6">
        <div className="h-6 bg-slate-200 rounded w-1/4 mb-4"></div>
        <div className="h-20 bg-slate-100 rounded"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 text-red-700 p-4 rounded-xl border border-red-200 mb-6">
        <p className="font-medium">Sales Forecast Notice:</p>
        <p className="text-sm">{error}</p>
      </div>
    );
  }

  const futureForecast = data?.future_only_forecast || [];
  const modelComparison = data?.model_comparison || [];
  const selectedModel = data?.model_used || "Prophet";

  return (
    <div className="bg-white rounded-xl shadow-sm p-6 border border-slate-200 mb-6">
      {/* Header with Actions */}
      <div className="flex flex-wrap items-center justify-between mb-4 pb-3 border-b border-slate-100 gap-3">
        <div>
          <div className="flex items-center space-x-2">
            <h2 className="text-xl font-bold text-slate-900">
              📈 Multi-Model Sales Forecasting & Intelligence
            </h2>
            <span className="px-2.5 py-0.5 text-xs font-bold rounded-full bg-indigo-100 text-indigo-800 border border-indigo-200">
              Day 7–10
            </span>
          </div>
          <p className="text-sm text-slate-500">
            Prophet vs Random Forest vs XGBoost Regressors with 30-Day Projections
          </p>
        </div>

        <div className="flex items-center space-x-2 flex-wrap gap-2">
          {/* View Mode Toggle */}
          <div className="inline-flex rounded-lg border border-slate-200 p-0.5 bg-slate-100">
            <button
              onClick={() => setViewMode("table")}
              className={`px-3 py-1 text-xs font-semibold rounded-md transition-all ${
                viewMode === "table"
                  ? "bg-white text-indigo-700 shadow-sm"
                  : "text-slate-600 hover:text-slate-900"
              }`}
            >
              Forecast Table
            </button>
            <button
              onClick={() => setViewMode("models")}
              className={`px-3 py-1 text-xs font-semibold rounded-md transition-all ${
                viewMode === "models"
                  ? "bg-white text-indigo-700 shadow-sm"
                  : "text-slate-600 hover:text-slate-900"
              }`}
            >
              Model Competition
            </button>
            <button
              onClick={() => setViewMode("chart")}
              className={`px-3 py-1 text-xs font-semibold rounded-md transition-all ${
                viewMode === "chart"
                  ? "bg-white text-indigo-700 shadow-sm"
                  : "text-slate-600 hover:text-slate-900"
              }`}
            >
              Plots & Components
            </button>
          </div>

          {/* Download Business Report Button */}
          <button
            onClick={handleDownloadReport}
            disabled={downloading}
            className="flex items-center space-x-1.5 px-3 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-semibold rounded-lg shadow-sm transition-colors disabled:opacity-50"
          >
            <span>📥</span>
            <span>{downloading ? "Generating..." : "Download Excel Report"}</span>
          </button>
        </div>
      </div>

      {/* KPI Stats Header */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <div className="p-4 bg-slate-50 rounded-xl border border-slate-200">
          <div className="text-xs text-slate-500 font-medium">Selected Forecast Model</div>
          <div className="text-lg font-extrabold text-indigo-700 mt-1">
            {selectedModel}
          </div>
          <div className="text-xs text-emerald-700 font-medium mt-1">
            ✓ Selected based on lowest evaluation error
          </div>
        </div>

        <div className="p-4 bg-slate-50 rounded-xl border border-slate-200">
          <div className="text-xs text-slate-500 font-medium">30-Day Projected Revenue</div>
          <div className="text-lg font-extrabold text-slate-900 mt-1">
            ₹{data?.predicted_revenue?.toFixed(2) || "0.00"}
          </div>
          <div className="text-xs text-slate-600 mt-1">
            Horizon: {data?.period || "Next 30 Days"}
          </div>
        </div>

        <div className="p-4 bg-slate-50 rounded-xl border border-slate-200">
          <div className="text-xs text-slate-500 font-medium">Historical Training Range</div>
          <div className="text-base font-bold text-slate-900 mt-1">
            {data?.historical_period?.start_date} to {data?.historical_period?.end_date}
          </div>
          <div className="text-xs text-slate-600 mt-1">
            {data?.historical_period?.recorded_days} Days Recorded
          </div>
        </div>

        <div className="p-4 bg-slate-50 rounded-xl border border-slate-200">
          <div className="text-xs text-slate-500 font-medium">Data Integrity Check</div>
          <div className="text-base font-bold text-slate-900 mt-1">
            {data?.missing_dates_summary?.count === 0 ? (
              <span className="text-emerald-700">0 Missing Dates</span>
            ) : (
              <span className="text-amber-700">{data?.missing_dates_summary?.count} Missing Dates</span>
            )}
          </div>
          <div className="text-xs text-slate-600 mt-1">
            Continuous daily series verified
          </div>
        </div>
      </div>

      {/* Limitation Warning */}
      {data?.limitations && (
        <div className="p-3 bg-amber-50 border border-amber-200 rounded-lg text-xs text-amber-800 mb-4 flex items-start space-x-2">
          <span className="font-bold">ℹ️ Note:</span>
          <span>{data.limitations}</span>
        </div>
      )}

      {/* Model Competition View */}
      {viewMode === "models" && (
        <div className="space-y-4">
          <div className="p-4 rounded-xl border border-slate-200 bg-slate-50">
            <h3 className="text-sm font-bold text-slate-900 mb-1">
              🏆 Multi-Model Regressor Comparison (Day 7–8)
            </h3>
            <p className="text-xs text-slate-600 mb-4">
              All models evaluated on identical chronological train/test splits. Lower MAE and RMSE indicate lower prediction error.
            </p>
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse text-sm">
                <thead>
                  <tr className="bg-slate-200 text-slate-700 font-semibold border-b border-slate-300">
                    <th className="py-2.5 px-3">Model</th>
                    <th className="py-2.5 px-3">MAE (Mean Absolute Error)</th>
                    <th className="py-2.5 px-3">RMSE (Root Mean Sq Error)</th>
                    <th className="py-2.5 px-3">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-200 bg-white">
                  {modelComparison.map((m, idx) => {
                    const isBest = m.model === selectedModel;
                    return (
                      <tr key={idx} className={isBest ? "bg-indigo-50/50 font-semibold" : ""}>
                        <td className="py-2.5 px-3 text-slate-900 flex items-center space-x-2">
                          <span>{m.model}</span>
                          {isBest && (
                            <span className="px-2 py-0.5 text-xs bg-emerald-100 text-emerald-800 border border-emerald-300 rounded-full font-bold">
                              Winner
                            </span>
                          )}
                        </td>
                        <td className="py-2.5 px-3 text-slate-700">{m.mae.toFixed(4)}</td>
                        <td className="py-2.5 px-3 text-slate-700">{m.rmse.toFixed(4)}</td>
                        <td className="py-2.5 px-3">
                          {isBest ? (
                            <span className="text-xs text-emerald-700 font-medium">
                              Selected (Lowest Error)
                            </span>
                          ) : (
                            <span className="text-xs text-slate-500">Evaluated</span>
                          )}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* Forecast Table View */}
      {viewMode === "table" && (
        <div className="overflow-x-auto max-h-96">
          <table className="w-full text-left border-collapse text-sm">
            <thead className="sticky top-0 bg-slate-100 text-slate-700 font-semibold border-b border-slate-200">
              <tr>
                <th className="py-2.5 px-3">Forecast Date</th>
                <th className="py-2.5 px-3">Predicted Revenue</th>
                <th className="py-2.5 px-3">Lower Bound</th>
                <th className="py-2.5 px-3">Upper Bound</th>
                <th className="py-2.5 px-3">Model Used</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {futureForecast.map((item, idx) => (
                <tr key={idx} className="hover:bg-slate-50 transition-colors">
                  <td className="py-2 px-3 font-mono font-medium text-slate-900">{item.ds}</td>
                  <td className="py-2 px-3 font-semibold text-indigo-700">
                    ₹{item.yhat.toFixed(2)}
                  </td>
                  <td className="py-2 px-3 text-slate-600">₹{item.yhat_lower.toFixed(2)}</td>
                  <td className="py-2 px-3 text-slate-600">₹{item.yhat_upper.toFixed(2)}</td>
                  <td className="py-2 px-3 text-slate-500 font-mono text-xs">{selectedModel}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Plots & Components View */}
      {viewMode === "chart" && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="p-4 border border-slate-200 rounded-xl bg-slate-50 text-center">
            <h4 className="text-sm font-bold text-slate-800 mb-2">30-Day Revenue Forecast Plot</h4>
            <img
              src="/reports/forecast_chart.png"
              alt="Forecast Chart"
              className="mx-auto rounded border border-slate-200 shadow-sm max-h-72 object-contain"
              onError={(e) => {
                e.target.style.display = 'none';
              }}
            />
            <p className="text-xs text-slate-500 mt-2">Saved under <code>reports/forecast_chart.png</code></p>
          </div>
          <div className="p-4 border border-slate-200 rounded-xl bg-slate-50 text-center">
            <h4 className="text-sm font-bold text-slate-800 mb-2">Forecast Trend & Seasonality Components</h4>
            <img
              src="/reports/forecast_components.png"
              alt="Forecast Components Chart"
              className="mx-auto rounded border border-slate-200 shadow-sm max-h-72 object-contain"
              onError={(e) => {
                e.target.style.display = 'none';
              }}
            />
            <p className="text-xs text-slate-500 mt-2">Saved under <code>reports/forecast_components.png</code></p>
          </div>
        </div>
      )}
    </div>
  );
}
