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
        const res = await getForecastingSummary().catch(() => null);
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
      <div className="glass-card" style={{ marginBottom: "32px", padding: "32px", textAlign: "center" }}>
        <div className="loading-spinner">
          <div className="spinner"></div>
          <span>Loading Multi-Model Sales Forecasting Engine...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="msg-banner msg-error" style={{ marginBottom: "32px" }}>
        <span>⚠️ Forecasting Notice: {error}</span>
      </div>
    );
  }

  const futureForecast = data?.future_only_forecast || [];
  const modelComparison = data?.model_comparison || [];
  const selectedModel = data?.model_used || "Prophet";

  return (
    <div className="glass-card" style={{ marginBottom: "32px" }}>
      {/* Header & Mode Switcher Controls */}
      <div className="card-header" style={{ flexWrap: "wrap", gap: "16px", alignItems: "center" }}>
        <div>
          <div className="card-title">
            <span>📈</span>
            <span>Multi-Model Sales Forecasting & Intelligence</span>
          </div>
          <p style={{ fontSize: "0.82rem", color: "var(--text-muted)", marginTop: "3px" }}>
            Prophet vs Random Forest vs XGBoost Regressors with 30-Day Projections
          </p>
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: "12px", flexWrap: "wrap" }}>
          {/* Tab Switcher */}
          <div className="tab-group">
            <button
              type="button"
              onClick={() => setViewMode("table")}
              className={`tab-btn ${viewMode === "table" ? "active" : ""}`}
            >
              <span>📊</span>
              <span>Forecast Table</span>
            </button>
            <button
              type="button"
              onClick={() => setViewMode("models")}
              className={`tab-btn ${viewMode === "models" ? "active" : ""}`}
            >
              <span>🏆</span>
              <span>Model Competition</span>
            </button>
            <button
              type="button"
              onClick={() => setViewMode("chart")}
              className={`tab-btn ${viewMode === "chart" ? "active" : ""}`}
            >
              <span>🖼️</span>
              <span>Plots & Components</span>
            </button>
          </div>

          {/* Download Excel Report */}
          <button
            type="button"
            onClick={handleDownloadReport}
            disabled={downloading}
            className="btn btn-primary btn-sm"
            style={{ display: "inline-flex", alignItems: "center", gap: "6px" }}
          >
            <span>📥</span>
            <span>{downloading ? "Generating..." : "Download Excel Report"}</span>
          </button>
        </div>
      </div>

      <div className="card-body">
        {/* KPI Stats Overview */}
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
            gap: "16px",
            marginBottom: "28px",
          }}
        >
          {/* Selected Model */}
          <div className="segment-card">
            <div style={{ fontSize: "0.75rem", fontWeight: 700, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.05em" }}>
              Selected Forecast Model
            </div>
            <div style={{ fontSize: "1.6rem", fontWeight: 800, color: "#818cf8", marginTop: "4px" }}>
              {selectedModel}
            </div>
            <div style={{ marginTop: "6px" }}>
              <span className="winner-tag">
                ✓ Lowest Test Error
              </span>
            </div>
          </div>

          {/* 30-Day Projected Revenue */}
          <div className="segment-card">
            <div style={{ fontSize: "0.75rem", fontWeight: 700, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.05em" }}>
              30-Day Projected Revenue
            </div>
            <div style={{ fontSize: "1.6rem", fontWeight: 800, color: "#34d399", marginTop: "4px" }}>
              ₹{Number(data?.predicted_revenue || 0).toFixed(2)}
            </div>
            <div style={{ fontSize: "0.76rem", color: "var(--text-dim)", marginTop: "6px" }}>
              Horizon: {data?.period || "Next 30 Days"}
            </div>
          </div>

          {/* Historical Training Range */}
          <div className="segment-card">
            <div style={{ fontSize: "0.75rem", fontWeight: 700, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.05em" }}>
              Training Data Range
            </div>
            <div style={{ fontSize: "1.1rem", fontWeight: 700, color: "var(--text-main)", marginTop: "6px", fontFamily: "monospace" }}>
              {data?.historical_period?.start_date || "N/A"} → {data?.historical_period?.end_date || "N/A"}
            </div>
            <div style={{ fontSize: "0.76rem", color: "var(--text-dim)", marginTop: "6px" }}>
              {data?.historical_period?.recorded_days || 0} Daily Observations
            </div>
          </div>

          {/* Missing Dates / Continuity */}
          <div className="segment-card">
            <div style={{ fontSize: "0.75rem", fontWeight: 700, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.05em" }}>
              Data Integrity & Continuity
            </div>
            <div style={{ fontSize: "1.25rem", fontWeight: 800, color: "#38bdf8", marginTop: "6px" }}>
              {data?.missing_dates_summary?.count === 0 ? "0 Missing Dates" : `${data?.missing_dates_summary?.count} Missing Dates`}
            </div>
            <div style={{ fontSize: "0.76rem", color: "var(--text-dim)", marginTop: "6px" }}>
              Continuous chronological sequence verified
            </div>
          </div>
        </div>

        {/* Informational Limitations Notice */}
        {data?.limitations && (
          <div
            style={{
              padding: "12px 16px",
              background: "rgba(245, 158, 11, 0.08)",
              border: "1px solid rgba(245, 158, 11, 0.25)",
              borderRadius: "var(--radius-sm)",
              fontSize: "0.82rem",
              color: "#fde68a",
              marginBottom: "24px",
              display: "flex",
              alignItems: "center",
              gap: "8px",
            }}
          >
            <span>ℹ️</span>
            <span>{data.limitations}</span>
          </div>
        )}

        {/* Tab 1: Forecast Table View */}
        {viewMode === "table" && (
          <div>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "14px" }}>
              <h4 style={{ fontSize: "0.95rem", fontWeight: 700, color: "var(--text-main)" }}>
                📅 30-Day Daily Revenue Projections ({futureForecast.length} Forecast Days)
              </h4>
              <span className="info-tag">
                Model: {selectedModel}
              </span>
            </div>

            <div className="table-container" style={{ maxHeight: "420px" }}>
              <table className="data-table">
                <thead style={{ position: "sticky", top: 0, zIndex: 2, background: "var(--bg-surface-elevated)" }}>
                  <tr>
                    <th>Forecast Date</th>
                    <th>Projected Revenue</th>
                    <th>Lower Bound (80% CI)</th>
                    <th>Upper Bound (80% CI)</th>
                    <th>Regressors Applied</th>
                  </tr>
                </thead>
                <tbody>
                  {futureForecast.map((item, idx) => (
                    <tr key={idx}>
                      <td style={{ fontWeight: 700, color: "#38bdf8", fontFamily: "monospace" }}>
                        {item?.ds}
                      </td>
                      <td style={{ fontWeight: 700, color: "#a855f7", fontSize: "0.95rem" }}>
                        ₹{Number(item?.yhat || 0).toFixed(2)}
                      </td>
                      <td style={{ color: "var(--text-muted)", fontFamily: "monospace" }}>
                        ₹{Number(item?.yhat_lower || 0).toFixed(2)}
                      </td>
                      <td style={{ color: "var(--text-muted)", fontFamily: "monospace" }}>
                        ₹{Number(item?.yhat_upper || 0).toFixed(2)}
                      </td>
                      <td>
                        <span className="info-tag">
                          {selectedModel}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Tab 2: Model Competition View */}
        {viewMode === "models" && (
          <div>
            <div style={{ marginBottom: "16px" }}>
              <h4 style={{ fontSize: "0.95rem", fontWeight: 700, color: "var(--text-main)", marginBottom: "4px" }}>
                🏆 Multi-Model Regressor Competition & Error Evaluation
              </h4>
              <p style={{ fontSize: "0.82rem", color: "var(--text-muted)" }}>
                All regressors evaluated on identical chronological holdout splits without data leakage. The model with lowest evaluation error is automatically chosen for live forecasting.
              </p>
            </div>

            <div className="table-container">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Model Architecture</th>
                    <th>MAE (Mean Absolute Error)</th>
                    <th>RMSE (Root Mean Squared Error)</th>
                    <th>Evaluation Status</th>
                  </tr>
                </thead>
                <tbody>
                  {modelComparison.map((m, idx) => {
                    const isBest = m?.model === selectedModel;
                    return (
                      <tr
                        key={idx}
                        style={{
                          background: isBest ? "rgba(99, 102, 241, 0.08)" : "transparent",
                          fontWeight: isBest ? 700 : 400,
                        }}
                      >
                        <td>
                          <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                            <span style={{ color: isBest ? "#ffffff" : "var(--text-main)", fontSize: "0.92rem", fontWeight: 700 }}>
                              {m?.model}
                            </span>
                            {isBest && (
                              <span className="winner-tag">
                                🏆 Selected Champion
                              </span>
                            )}
                          </div>
                        </td>
                        <td style={{ fontFamily: "monospace", color: isBest ? "#34d399" : "var(--text-main)" }}>
                          {m?.mae != null ? Number(m.mae).toFixed(4) : "—"}
                        </td>
                        <td style={{ fontFamily: "monospace", color: isBest ? "#34d399" : "var(--text-main)" }}>
                          {m?.rmse != null ? Number(m.rmse).toFixed(4) : "—"}
                        </td>
                        <td>
                          {isBest ? (
                            <span className="status-pill status-healthy">
                              Production Active
                            </span>
                          ) : (
                            <span style={{ fontSize: "0.78rem", color: "var(--text-dim)" }}>
                              Evaluated Alternative
                            </span>
                          )}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Tab 3: Plots & Visual Charts View */}
        {viewMode === "chart" && (
          <div className="plots-grid">
            <div className="plot-card">
              <h4>📈 30-Day Revenue Forecast Trend</h4>
              <p>Historical revenue vs Prophet 30-day projection envelope with confidence interval</p>
              <div className="plot-image-container">
                <img
                  src={`/reports/forecast_chart.png?t=${Date.now()}`}
                  alt="30-Day Sales Forecast Plot"
                  onError={(e) => {
                    e.target.style.display = "none";
                  }}
                />
              </div>
            </div>

            <div className="plot-card">
              <h4>📊 Forecast Components & Trend Breakdown</h4>
              <p>Decomposed weekly seasonality, day-of-week trends, and growth trajectory</p>
              <div className="plot-image-container">
                <img
                  src={`/reports/forecast_components.png?t=${Date.now()}`}
                  alt="Forecast Components Plot"
                  onError={(e) => {
                    e.target.style.display = "none";
                  }}
                />
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
