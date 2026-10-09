import FilterBar from "../components/FilterBar";
import { IconForecasting, IconSales } from "../components/Icons";
import "./ForecastingPage.css";

export default function ForecastingPage({
  filters,
  setFilters,
  filterOptions,
  resetFilters,
  canViewForecast,
  forecastData,
  forecastHorizon,
  setForecastHorizon,
  forecastModel,
  setForecastModel,
  renderForecastChart,
}) {
  if (!canViewForecast) {
    return (
      <div className="page-container fcst-page-wrap">
        <div className="fcst-card">
          <h2 className="fcst-card-title">Access Restricted</h2>
          <p className="fcst-card-sub">
            Sales Forecasting is available to Store Managers, Business Owners,
            and Administrators only.
          </p>
        </div>
      </div>
    );
  }

  const summary = forecastData?.summary_metrics || {};
  const projTotal = Number(summary.projected_period_total_revenue || 0);
  const growthPct = Number(summary.projected_growth_pct || 0);
  const histAvg = Number(summary.historical_avg_daily_revenue || 0);
  const projDailyAvg = forecastHorizon > 0 ? projTotal / forecastHorizon : 0;

  const growthTone =
    growthPct > 2 ? "positive" : growthPct < -2 ? "negative" : "stable";
  const modelUsed = forecastData?.model_used || "—";

  const modelComparison = forecastData?.model_comparison || [];
  const bestModel = modelComparison.reduce(
    (best, m) => (!best || m.r2_score > best.r2_score ? m : best),
    null
  );

  const growthDirection =
    growthPct > 2
      ? "Revenue is expected to increase over the selected forecast period."
      : growthPct < -2
      ? "Revenue is expected to decrease over the selected forecast period."
      : "Revenue is expected to remain relatively stable over the selected forecast period.";

  const planningDirection =
    growthTone === "positive"
      ? "Plan for higher expected sales activity during the forecast period."
      : growthTone === "negative"
        ? "Review upcoming sales and inventory plans for the forecast period."
        : "Maintain current operating plans while monitoring actual sales against the forecast.";

  const formattedRevenue = `₹${projTotal.toLocaleString(undefined, {
    maximumFractionDigits: 0,
  })}`;
  const formattedHistoricalDailyRevenue = `₹${histAvg.toLocaleString(undefined, {
    maximumFractionDigits: 0,
  })}`;
  const formattedProjectedDailyRevenue = `₹${projDailyAvg.toLocaleString(undefined, {
    maximumFractionDigits: 0,
  })}`;
  const formattedGrowth = `${growthPct > 0 ? "+" : ""}${growthPct}%`;

  return (
    <div className="page-container fcst-page-wrap">
      {/* 1. PAGE HEADER */}
      <div className="fcst-header-block">
        <h1 className="fcst-main-title">
          <span className="fcst-title-icon"><IconForecasting size={20} color="#4776e6" /></span> Sales Forecast
        </h1>
        <p className="fcst-main-subtitle">
          Understand expected revenue and plan upcoming business activity.
        </p>
        <p className="fcst-header-note">
          Use historical sales patterns to estimate future revenue for the selected period.
        </p>
      </div>

      <FilterBar
        filters={filters}
        setFilters={setFilters}
        filterOptions={filterOptions}
        resetFilters={resetFilters}
      />

      {/* 2. FORECAST CONTROLS */}
      <div className="fcst-controls-card">
        <div className="fcst-settings-heading">
          <h2>Forecast Settings</h2>
          <p>Choose the forecasting approach and how far ahead you want to plan.</p>
        </div>
        <div className="fcst-controls-row">
          <div className="fcst-control-group">
            <span className="fcst-control-label">Forecast Model</span>
            <div className="toggle-group-compact">
              {["prophet", "xgboost", "random_forest"].map((m) => (
                <button
                  key={m}
                  className={`toggle-btn-sm ${forecastModel === m ? "active" : ""}`}
                  onClick={() => setForecastModel(m)}
                >
                  {m === "prophet"
                    ? "Prophet"
                    : m === "xgboost"
                    ? "XGBoost"
                    : "Random Forest"}
                </button>
              ))}
            </div>
          </div>

          <div className="fcst-control-group">
            <span className="fcst-control-label">Forecast Period</span>
            <div className="toggle-group-compact">
              {[30, 60, 90].map((h) => (
                <button
                  key={h}
                  className={`toggle-btn-sm ${forecastHorizon === h ? "active" : ""}`}
                  onClick={() => setForecastHorizon(h)}
                >
                  {h} Days
                </button>
              ))}
            </div>
          </div>

          <div className="fcst-engine-pill-wrap">
            <span className="fcst-engine-pill">
              Engine: {modelUsed}
            </span>
          </div>
        </div>
      </div>

      {/* 3. KPI CARDS */}
      <div className="fcst-summary-heading">
        <div>
          <h2>Forecast Summary</h2>
          <p>Expected revenue based on the selected filters and forecast period.</p>
        </div>
      </div>
      <div className="fcst-kpi-grid">
        <div className="fcst-kpi-card card-fcst-blue">
          <div className="fcst-kpi-top">
            <span className="fcst-kpi-label">Forecast Revenue</span>
            <span className="fcst-kpi-icon fcst-icon-blue"><IconSales size={16} /></span>
          </div>
          <div className="fcst-kpi-value text-primary">
            {formattedRevenue}
          </div>
          <span className="fcst-kpi-subtext">
            Projected revenue for {forecastHorizon} days
          </span>
        </div>

        <div className="fcst-kpi-card card-fcst-growth">
          <div className="fcst-kpi-top">
            <span className="fcst-kpi-label">Expected Growth</span>
            <span className={`fcst-kpi-icon fcst-icon-${growthTone}`}><IconForecasting size={16} /></span>
          </div>
          <div className={`fcst-kpi-value fcst-growth-${growthTone}`}>
            {formattedGrowth}
          </div>
          <span className="fcst-kpi-subtext">Compared with historical daily revenue</span>
        </div>

        <div className="fcst-kpi-card card-fcst-horizon">
          <div className="fcst-kpi-top">
            <span className="fcst-kpi-label">Forecast Horizon</span>
            <span className="fcst-kpi-icon fcst-icon-amber"><IconForecasting size={16} /></span>
          </div>
          <div className="fcst-kpi-value fcst-value-amber">
            {forecastHorizon} Days
          </div>
          <span className="fcst-kpi-subtext">
            Selected planning period
          </span>
        </div>

        <div className="fcst-kpi-card card-fcst-avg">
          <div className="fcst-kpi-top">
            <span className="fcst-kpi-label">Average Daily Revenue</span>
            <span className="fcst-kpi-icon fcst-icon-purple"><IconSales size={16} /></span>
          </div>
          <div className="fcst-kpi-value fcst-value-purple">
            {formattedHistoricalDailyRevenue}
          </div>
          <span className="fcst-kpi-subtext">
            Projected daily average: {formattedProjectedDailyRevenue}
          </span>
        </div>
      </div>

      {/* 4. BUSINESS INTERPRETATION */}
      <section className={`fcst-meaning-card fcst-meaning-${growthTone}`}>
        <div className="fcst-meaning-heading">
          <div>
            <span className="fcst-eyebrow">Business interpretation</span>
            <h2>What This Forecast Means</h2>
          </div>
          <span className={`fcst-meaning-state fcst-meaning-state-${growthTone}`}>
            {growthTone === "positive" ? "Growth expected" : growthTone === "negative" ? "Decline expected" : "Relatively stable"}
          </span>
        </div>
        <div className="fcst-meaning-metrics">
          <div><span>Expected revenue</span><strong>{formattedRevenue}</strong></div>
          <div><span>Expected growth</span><strong className={`fcst-growth-${growthTone}`}>{formattedGrowth}</strong></div>
          <div><span>Forecast period</span><strong>{forecastHorizon} days</strong></div>
        </div>
        <p className="fcst-meaning-copy">{growthDirection}</p>
        <p className="fcst-meaning-note">Use this estimate to support upcoming sales and inventory planning.</p>
      </section>

      {/* 5. MAIN CHART */}
      <div className="fcst-card fcst-chart-card">
        <div className="fcst-section-header">
          <div>
            <h3 className="fcst-card-title"><IconSales size={17} color="#4776e6" />Revenue Forecast</h3>
            <p className="fcst-card-sub">
              Historical revenue and predicted revenue for the selected forecast period.
            </p>
          </div>
        </div>
        {renderForecastChart()}
        <div className="fcst-chart-explainer">
          <div>
            <span className="fcst-explainer-symbol fcst-symbol-history" />
            <strong>Historical</strong>
            <p>Actual recorded sales used by the model.</p>
          </div>
          <div>
            <span className="fcst-explainer-symbol fcst-symbol-forecast" />
            <strong>Forecast</strong>
            <p>Expected future revenue for the selected period.</p>
          </div>
          <div>
            <span className="fcst-explainer-symbol fcst-symbol-interval" />
            <strong>Confidence interval</strong>
            <p>Expected range around the forecast.</p>
          </div>
        </div>
        <p className="fcst-chart-note">Shaded area represents the forecast uncertainty range.</p>
      </div>

      {/* 6. PLANNING VIEW */}
      <section className="fcst-planning-card">
        <div className="fcst-section-header">
          <div>
            <span className="fcst-eyebrow">Business planning</span>
            <h2 className="fcst-card-title">Planning View</h2>
          </div>
        </div>
        <div className="fcst-planning-metrics">
          <div><span>Forecast period</span><strong>{forecastHorizon} days</strong></div>
          <div><span>Expected growth</span><strong className={`fcst-growth-${growthTone}`}>{formattedGrowth}</strong></div>
          <div><span>Projected revenue</span><strong>{formattedRevenue}</strong></div>
        </div>
        <p>{planningDirection}</p>
      </section>

      {/* 7. MODEL PERFORMANCE */}
      {modelComparison.length > 0 && (
        <div className="fcst-card">
          <div className="fcst-section-header">
            <div>
              <h3 className="fcst-card-title">Forecast Model Performance</h3>
              <p className="fcst-card-sub">
                Comparison of model accuracy using the existing evaluation results.
              </p>
            </div>
            {bestModel && (
              <span className="fcst-engine-pill">
                Highest R²: {bestModel.model} ({bestModel.r2_score})
              </span>
            )}
          </div>

          <div className="table-responsive">
            <table className="fcst-model-table">
              <thead>
                <tr>
                  <th>Model</th>
                  <th>MAE</th>
                  <th>RMSE</th>
                  <th>R² Score</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {modelComparison.map((m) => {
                  const isActive = modelUsed
                    .toLowerCase()
                    .includes(m.model.toLowerCase());
                  return (
                    <tr
                      key={m.model}
                      className={`${isActive ? "fcst-row-active" : ""}${m === bestModel ? " fcst-row-best" : ""}`}
                    >
                      <td>
                        <strong>{m.model}</strong>
                      </td>
                      <td>{m.mae?.toLocaleString()}</td>
                      <td>{m.rmse?.toLocaleString()}</td>
                      <td className="font-bold text-primary">{m.r2_score}</td>
                      <td>
                        {isActive ? (
                          <span className="badge-teal">Active</span>
                        ) : (
                          <span className="text-muted" style={{ fontSize: "11.5px" }}>
                            Evaluated
                          </span>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
          <p className="fcst-model-note">
            Lower MAE and RMSE generally indicate smaller prediction errors. R² is shown as the existing model evaluation metric.
          </p>
        </div>
      )}
    </div>
  );
}
