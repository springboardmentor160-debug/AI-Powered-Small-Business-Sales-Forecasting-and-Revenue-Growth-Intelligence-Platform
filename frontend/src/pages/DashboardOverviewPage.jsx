import FilterBar from "../components/FilterBar";
import {
  IconArrowRight,
  IconChurn,
  IconSales,
} from "../components/Icons";

const segmentColors = ["#4776e6", "#8b5cf6", "#16a683", "#f3a43b", "#e76f8a"];

function DataState({ status, emptyMessage, loadingMessage = "Loading data..." }) {
  const messages = {
    loading: loadingMessage,
    empty: emptyMessage,
    error: "Unable to load this data. Try again or adjust the filters.",
    restricted: "Access is restricted for your role.",
  };

  return (
    <div className={`dash-data-state dash-data-state-${status}`} role="status">
      {messages[status] || emptyMessage}
    </div>
  );
}

function KpiCard({ label, value, detail, status, tone }) {
  const stateValue = {
    loading: "Loading",
    empty: "No data",
    error: "Unavailable",
    restricted: "Restricted",
  };

  return (
    <section className={`dash-kpi-card dash-kpi-${tone}`}>
      <div className="dash-kpi-top">
        <span className="dash-kpi-label">{label}</span>
        <span className={`dash-kpi-indicator dash-kpi-indicator-${tone}`} aria-hidden="true" />
      </div>
      <div className={`dash-kpi-value ${status === "ready" ? "" : "dash-kpi-state-value"}`}>
        {status === "ready" ? value : stateValue[status] || "Unavailable"}
      </div>
      {status === "ready" && detail && (
        <span className="dash-kpi-subtext">{detail}</span>
      )}
      {(status === "error" || status === "restricted") && (
        <span className="dash-kpi-subtext">{status === "restricted" ? "Role access" : "Data unavailable"}</span>
      )}
      {status === "empty" && <span className="dash-kpi-subtext">No matching records</span>}
      {status === "loading" && <span className="dash-kpi-subtext">Updating</span>}
    </section>
  );
}

function formatCurrency(value) {
  return `₹${Number(value).toLocaleString("en-IN", { maximumFractionDigits: 0 })}`;
}

function getProbabilityValue(value) {
  const probability = Number.parseFloat(String(value).replace("%", ""));
  if (!Number.isFinite(probability)) return null;
  return probability > 0 && probability < 1 ? probability * 100 : probability;
}

function getRiskLevel(probability) {
  if (probability >= 70) return "High";
  if (probability >= 40) return "Medium";
  return "Low";
}

function ForecastChart({ forecastData }) {
  const historical = (forecastData?.historical_data || [])
    .filter((point) => point.y !== null && point.y !== undefined && Number.isFinite(Number(point.y)))
    .slice(-12);
  const forecast = (forecastData?.forecast_data || [])
    .filter((point) => point.yhat !== null && point.yhat !== undefined && Number.isFinite(Number(point.yhat)))
    .slice(0, 12);
  const values = [
    ...historical.map((point) => Number(point.y)),
    ...forecast.map((point) => Number(point.yhat)),
  ];

  if (!values.length) {
    return <DataState status="empty" emptyMessage="No forecast series is available for these filters." />;
  }

  const width = 620;
  const height = 190;
  const padding = { top: 12, right: 12, bottom: 24, left: 12 };
  const plotWidth = width - padding.left - padding.right;
  const plotHeight = height - padding.top - padding.bottom;
  const maximum = Math.max(...values, 1) * 1.08;
  const pointCount = historical.length + forecast.length;
  const pointX = (index) =>
    padding.left + (pointCount <= 1 ? plotWidth / 2 : (index / (pointCount - 1)) * plotWidth);
  const pointY = (value) => height - padding.bottom - (Number(value) / maximum) * plotHeight;
  const historicalPoints = historical.map((point, index) => `${pointX(index)},${pointY(point.y)}`);
  const forecastPoints = forecast.map((point, index) =>
    `${pointX(historical.length + index)},${pointY(point.yhat)}`
  );
  const forecastLine = historicalPoints.length
    ? [historicalPoints[historicalPoints.length - 1], ...forecastPoints].join(" ")
    : forecastPoints.join(" ");
  const growth = forecastData?.summary_metrics?.projected_growth_pct;
  const hasGrowth =
    growth !== undefined &&
    growth !== null &&
    growth !== "" &&
    Number.isFinite(Number(growth));

  return (
    <div className="dash-forecast-chart-wrap">
      {hasGrowth && (
        <span className="dash-forecast-growth">
          Expected growth {Number(growth).toLocaleString("en-IN")}%
        </span>
      )}
      <svg
        className="dash-forecast-chart"
        viewBox={`0 0 ${width} ${height}`}
        role="img"
        aria-label="Historical sales and forecast chart"
      >
        {[0, 0.5, 1].map((ratio) => {
          const y = height - padding.bottom - ratio * plotHeight;
          return (
            <line
              key={ratio}
              x1={padding.left}
              y1={y}
              x2={width - padding.right}
              y2={y}
              className="dash-chart-gridline"
            />
          );
        })}
        {historicalPoints.length > 1 && (
          <polyline points={historicalPoints.join(" ")} className="dash-forecast-history-line" />
        )}
        {forecastLine && (
          <polyline points={forecastLine} className="dash-forecast-projection-line" />
        )}
        {historical.length > 0 && forecast.length > 0 && (
          <line
            x1={pointX(historical.length - 1)}
            y1={padding.top}
            x2={pointX(historical.length - 1)}
            y2={height - padding.bottom}
            className="dash-forecast-split"
          />
        )}
        <text x={padding.left} y={height - 4} className="dash-chart-date">
          {historical[0]?.ds || forecast[0]?.ds || ""}
        </text>
        <text x={width - padding.right} y={height - 4} textAnchor="end" className="dash-chart-date">
          {forecast[forecast.length - 1]?.ds || historical[historical.length - 1]?.ds || ""}
        </text>
      </svg>
      <div className="dash-chart-legend">
        {historical.length > 0 && <span><i className="dash-legend-dot dash-legend-history" />Historical</span>}
        {forecast.length > 0 && <span><i className="dash-legend-dot dash-legend-forecast" />Forecast</span>}
      </div>
    </div>
  );
}

export default function DashboardOverviewPage({
  revenue,
  margin,
  lowStock,
  canViewRevenue,
  canViewMargin,
  canViewLowStock,
  canViewForecast,
  filters,
  setFilters,
  filterOptions,
  resetFilters,
  renderTrendChart,
  trendGranularity,
  setTrendGranularity,
  forecastData,
  segmentationData,
  segmentationMethod,
  churnData,
  anomalyData,
  dashboardDataStatus,
  dashboardRequestKey,
  selectedModules = [
    "sales",
    "forecasting",
    "segmentation",
    "churn",
    "recommendations",
    "anomalies",
    "inventory",
    "reports",
  ],
  setActivePage,
}) {
  const hasModule = (module) =>
    selectedModules.length === 0 || selectedModules.includes(module);
  const statuses = dashboardDataStatus || {};
  const dataStatus = (key) =>
    statuses[key]?.requestKey === dashboardRequestKey
      ? statuses[key].status
      : "loading";
  const currentProfiles =
    segmentationMethod === "hierarchical"
      ? segmentationData?.hierarchical_profiles || []
      : segmentationData?.kmeans_profiles || [];
  const positiveSegments = currentProfiles
    .map((segment, index) => ({
      ...segment,
      color: segmentColors[index % segmentColors.length],
      share: Math.max(0, Number(segment.percentage) || 0),
    }))
    .filter((segment) => segment.share > 0);
  const segmentShareTotal = positiveSegments.reduce((sum, segment) => sum + segment.share, 0);
  const donutStops = positiveSegments.reduce(
    (result, segment) => {
      const end = result.offset + (segment.share / segmentShareTotal) * 100;
      return {
        offset: end,
        stops: [...result.stops, `${segment.color} ${result.offset}% ${end}%`],
      };
    },
    { offset: 0, stops: [] }
  ).stops.join(", ");
  const segmentationStatus =
    dataStatus("segmentation") === "ready" && currentProfiles.length === 0
    ? "empty"
    : dataStatus("segmentation");

  const cohortRisk = churnData?.churn_risk_by_segment_cohort || [];
  const highRiskRecords = churnData?.sample_high_risk_invoices || [];
  const churnRows = cohortRisk.length
    ? cohortRisk.slice(0, 5).map((cohort) => ({
        name: cohort.segment_name,
        probability: cohort.mean_churn_probability_pct,
      }))
    : highRiskRecords.slice(0, 5).map((record) => ({
        name: record.segment_name,
        probability: record.churn_risk_pct,
      }));

  return (
    <div className="page-container dash-page-wrap">
      <FilterBar
        filters={filters}
        setFilters={setFilters}
        filterOptions={filterOptions}
        resetFilters={resetFilters}
      />

      <div className="dash-kpi-grid">
        {hasModule("sales") && <KpiCard
          label="Total Sales / Revenue"
          value={formatCurrency(revenue)}
          detail="Across current filters"
          status={canViewRevenue ? dataStatus("revenue") : "restricted"}
          tone="revenue"
        />}
        {hasModule("sales") && <KpiCard
          label="Total Margin"
          value={formatCurrency(margin)}
          detail="Across current filters"
          status={canViewMargin ? dataStatus("margin") : "restricted"}
          tone="margin"
        />}
        {hasModule("segmentation") && <KpiCard
          label="Customer Cohorts"
          value={`${currentProfiles.length.toLocaleString()} segments`}
          detail="Groups identified by segmentation"
          status={segmentationStatus}
          tone="cohorts"
        />}
        {hasModule("inventory") && <KpiCard
          label="Low Stock Items"
          value={Number(lowStock).toLocaleString("en-IN")}
          detail="Items needing attention"
          status={canViewLowStock ? dataStatus("stock") : "restricted"}
          tone="stock"
        />}
      </div>

      <div className="dash-analytics-grid dash-main-analytics">
        {hasModule("sales") && <section className="dash-card dash-sales-card">
          <div className="dash-section-header">
            <div>
              <h2 className="dash-card-title"><IconSales size={17} color="#4776e6" />Sales Overview</h2>
              <p className="dash-card-sub">Revenue over time for the selected filters</p>
            </div>
            <div className="dash-card-actions">
              <div className="toggle-group-compact" aria-label="Sales trend period">
                <button
                  className={`toggle-btn-sm ${trendGranularity === "monthly" ? "active" : ""}`}
                  onClick={() => setTrendGranularity("monthly")}
                >
                  Monthly
                </button>
                <button
                  className={`toggle-btn-sm ${trendGranularity === "quarterly" ? "active" : ""}`}
                  onClick={() => setTrendGranularity("quarterly")}
                >
                  Quarterly
                </button>
              </div>
              <button className="btn-link-action" onClick={() => setActivePage("sales")}>
                View Sales <IconArrowRight size={13} />
              </button>
            </div>
          </div>
          {dataStatus("trends") === "ready" ? (
            renderTrendChart()
          ) : (
            <DataState
              status={dataStatus("trends")}
              loadingMessage="Loading sales history..."
              emptyMessage="No sales trend is available for these filters."
            />
          )}
        </section>}

        {hasModule("segmentation") && <section className="dash-card dash-segment-card">
          <div className="dash-section-header">
            <div>
              <h2 className="dash-card-title">Customer Segments</h2>
              <p className="dash-card-sub">Share by cohort, based on available sales records</p>
            </div>
            <button className="btn-link-action" onClick={() => setActivePage("segmentation")}>
              View Segments <IconArrowRight size={13} />
            </button>
          </div>
          {segmentationStatus === "ready" && positiveSegments.length > 0 ? (
            <div className="dash-segment-content">
              <div
                className="dash-segment-donut"
                style={{ background: `conic-gradient(${donutStops})` }}
                role="img"
                aria-label="Customer segment distribution"
              >
                <div className="dash-donut-center">
                  <strong>{currentProfiles.length}</strong>
                  <span>segments</span>
                </div>
              </div>
              <div className="dash-segment-legend">
                {positiveSegments.map((segment) => (
                  <div className="dash-segment-legend-row" key={segment.cluster_id ?? segment.segment_name}>
                    <span className="dash-segment-name">
                      <i style={{ backgroundColor: segment.color }} />
                      <span title={segment.segment_name}>{segment.segment_name}</span>
                    </span>
                    <span className="dash-segment-share">{segment.percentage}%</span>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <DataState
              status={segmentationStatus}
              loadingMessage="Loading customer cohorts..."
              emptyMessage="No segment distribution is available for these filters."
            />
          )}
        </section>}
      </div>

      <div className="dash-analytics-grid dash-secondary-analytics">
        {hasModule("forecasting") && <section className="dash-card">
          <div className="dash-section-header">
            <div>
              <h2 className="dash-card-title">Sales Forecast</h2>
              <p className="dash-card-sub">
                {forecastData?.forecast_horizon_days
                  ? `Historical and projected revenue · ${forecastData.forecast_horizon_days} day horizon`
                  : "Historical and projected revenue"}
              </p>
            </div>
            <button
              className="btn-link-action"
              onClick={() => setActivePage("forecasting")}
              disabled={!canViewForecast}
            >
              View Forecast <IconArrowRight size={13} />
            </button>
          </div>
          {canViewForecast ? (
            dataStatus("forecast") === "ready" ? (
              <ForecastChart forecastData={forecastData} />
            ) : (
              <DataState
                status={dataStatus("forecast")}
                loadingMessage="Loading sales forecast..."
                emptyMessage="No forecast series is available for these filters."
              />
            )
          ) : (
            <DataState status="restricted" emptyMessage="Forecast access is restricted." />
          )}
        </section>}

        {hasModule("churn") && <section className="dash-card">
          <div className="dash-section-header">
            <div>
              <h2 className="dash-card-title"><IconChurn size={17} color="#d78b27" />Churn Risk</h2>
              <p className="dash-card-sub">At-risk customer cohorts from churn analysis</p>
            </div>
            <button className="btn-link-action" onClick={() => setActivePage("churn")}>
              View All <IconArrowRight size={13} />
            </button>
          </div>
          {dataStatus("churn") === "ready" && churnRows.length > 0 ? (
            <div className="dash-risk-table-wrap">
              <table className="dash-risk-table">
                <thead>
                  <tr>
                    <th>Risk subject / cohort</th>
                    <th>Churn probability</th>
                    <th>Risk level</th>
                  </tr>
                </thead>
                <tbody>
                  {churnRows.map((row, index) => {
                    const probability = getProbabilityValue(row.probability);
                    const level = probability === null ? "Unknown" : getRiskLevel(probability);
                    return (
                      <tr key={`${row.name}-${index}`}>
                        <td title={row.name}>{row.name || "Unspecified cohort"}</td>
                        <td>{row.probability ?? "Not available"}</td>
                        <td><span className={`dash-risk-badge dash-risk-${level.toLowerCase()}`}>{level}</span></td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          ) : (
            <DataState
              status={dataStatus("churn")}
              loadingMessage="Loading churn risk..."
              emptyMessage="No at-risk cohorts are available for these filters."
            />
          )}
        </section>}
      </div>

      <section className="dash-alert-strip" aria-label="Business alerts">
        {hasModule("inventory") && <button className="dash-alert-item" onClick={() => setActivePage("inventory")}>
          <span className="dash-alert-dot dash-alert-dot-stock" />
          <span>Low stock</span>
          <strong>
            {canViewLowStock && dataStatus("stock") === "ready"
              ? Number(lowStock).toLocaleString("en-IN")
              : canViewLowStock
                ? dataStatus("stock") === "loading" ? "Loading" : dataStatus("stock") === "restricted" ? "Restricted" : "Unavailable"
                : "Restricted"}
          </strong>
          <IconArrowRight size={13} />
        </button>}
        {hasModule("churn") && <button className="dash-alert-item" onClick={() => setActivePage("churn")}>
          <span className="dash-alert-dot dash-alert-dot-churn" />
          <span>Churn risk</span>
          <strong>
            {dataStatus("churn") === "ready"
              ? churnData?.risk_distribution?.["High Risk"]?.count != null
                ? Number(churnData.risk_distribution["High Risk"].count).toLocaleString("en-IN")
                : "See cohorts"
              : dataStatus("churn") === "loading" ? "Loading" : dataStatus("churn") === "empty" ? "No data" : "Unavailable"}
          </strong>
          <IconArrowRight size={13} />
        </button>}
        {hasModule("anomalies") && <button className="dash-alert-item" onClick={() => setActivePage("anomalies")}>
          <span className="dash-alert-dot dash-alert-dot-anomaly" />
          <span>Anomalies</span>
          <strong>
            {dataStatus("anomalies") === "ready"
              ? Number.isFinite(anomalyData?.total_anomalies_detected)
                ? Number(anomalyData.total_anomalies_detected).toLocaleString("en-IN")
                : "Unavailable"
              : dataStatus("anomalies") === "loading"
                ? "Loading"
                : dataStatus("anomalies") === "empty"
                  ? "No data"
                  : dataStatus("anomalies") === "restricted"
                    ? "Restricted"
                    : "Unavailable"}
          </strong>
          <IconArrowRight size={13} />
        </button>}
      </section>
    </div>
  );
}
