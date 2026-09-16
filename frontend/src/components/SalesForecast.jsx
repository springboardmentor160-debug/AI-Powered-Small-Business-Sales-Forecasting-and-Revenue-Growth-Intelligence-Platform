import React, { useEffect, useState } from "react";
import { getForecastingSummary } from "../api";

export default function SalesForecast() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [viewMode, setViewMode] = useState("table"); // 'table' or 'chart'

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

  return (
    <div className="bg-white rounded-xl shadow-sm p-6 border border-slate-200 mb-6">
      <div className="flex flex-wrap items-center justify-between mb-4 pb-3 border-b border-slate-100">
        <div>
          <h2 className="text-xl font-bold text-slate-900">
            📈 Time-Series Sales Forecasting (Prophet)
          </h2>
          <p className="text-sm text-slate-500">
            30-Day Revenue Predictions with Uncertainty Intervals (Day 5–6)
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <button
            onClick={() => setViewMode("table")}
            className={`px-3 py-1 text-xs font-semibold rounded-lg border transition-colors ${
              viewMode === "table"
                ? "bg-indigo-600 text-white border-indigo-600"
                : "bg-white text-slate-700 border-slate-300 hover:bg-slate-50"
            }`}
          >
            Forecast Table
          </button>
          <button
            onClick={() => setViewMode("chart")}
            className={`px-3 py-1 text-xs font-semibold rounded-lg border transition-colors ${
              viewMode === "chart"
                ? "bg-indigo-600 text-white border-indigo-600"
                : "bg-white text-slate-700 border-slate-300 hover:bg-slate-50"
            }`}
          >
            Plots & Components
          </button>
        </div>
      </div>

      {/* KPI Stats Header */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
        <div className="p-4 bg-slate-50 rounded-xl border border-slate-200">
          <div className="text-xs text-slate-500 font-medium">Historical Range</div>
          <div className="text-base font-bold text-slate-900 mt-1">
            {data?.historical_period?.start_date} to {data?.historical_period?.end_date}
          </div>
          <div className="text-xs text-slate-600 mt-1">
            {data?.historical_period?.recorded_days} Days Recorded
          </div>
        </div>

        <div className="p-4 bg-slate-50 rounded-xl border border-slate-200">
          <div className="text-xs text-slate-500 font-medium">Missing Dates Check</div>
          <div className="text-base font-bold text-slate-900 mt-1">
            {data?.missing_dates_summary?.count === 0 ? (
              <span className="text-emerald-700">0 Missing Dates (Complete)</span>
            ) : (
              <span className="text-amber-700">{data?.missing_dates_summary?.count} Missing Dates</span>
            )}
          </div>
          <div className="text-xs text-slate-600 mt-1">
            Daily continuous revenue verified
          </div>
        </div>

        <div className="p-4 bg-slate-50 rounded-xl border border-slate-200">
          <div className="text-xs text-slate-500 font-medium">Forecast Horizon</div>
          <div className="text-base font-bold text-slate-900 mt-1">
            +{data?.forecast_horizon} Days
          </div>
          <div className="text-xs text-slate-600 mt-1">
            Calculated via Meta Prophet
          </div>
        </div>
      </div>

      {/* Limitation Warning */}
      {data?.limitations && (
        <div className="p-3 bg-amber-50 border border-amber-200 rounded-lg text-xs text-amber-800 mb-4 flex items-start space-x-2">
          <span className="font-bold">⚠️ Note:</span>
          <span>{data.limitations}</span>
        </div>
      )}

      {/* Content View */}
      {viewMode === "table" ? (
        <div className="overflow-x-auto max-h-96">
          <table className="w-full text-left border-collapse text-sm">
            <thead className="sticky top-0 bg-slate-100 text-slate-700 font-semibold border-b border-slate-200">
              <tr>
                <th className="py-2.5 px-3">Date (ds)</th>
                <th className="py-2.5 px-3">Predicted Revenue (yhat)</th>
                <th className="py-2.5 px-3">Lower Bound (yhat_lower)</th>
                <th className="py-2.5 px-3">Upper Bound (yhat_upper)</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {futureForecast.map((item, idx) => (
                <tr key={idx} className="hover:bg-slate-50 transition-colors">
                  <td className="py-2 px-3 font-mono font-medium text-slate-900">{item.ds}</td>
                  <td className="py-2 px-3 font-semibold text-indigo-700">
                    ${item.yhat.toFixed(2)}
                  </td>
                  <td className="py-2 px-3 text-slate-600">${item.yhat_lower.toFixed(2)}</td>
                  <td className="py-2 px-3 text-slate-600">${item.yhat_upper.toFixed(2)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="p-4 border border-slate-200 rounded-xl bg-slate-50 text-center">
            <h4 className="text-sm font-bold text-slate-800 mb-2">30-Day Revenue Forecast Plot</h4>
            <img
              src="/reports/forecast_chart.png"
              alt="Prophet Forecast Chart"
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
              alt="Prophet Components Chart"
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
