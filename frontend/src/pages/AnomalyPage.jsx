import React from "react";
import FilterBar from "../components/FilterBar";
import { IconAnomaly } from "../components/Icons";

export default function AnomalyPage({
  filters,
  setFilters,
  filterOptions,
  resetFilters,
  anomalyData,
}) {
  if (!anomalyData) {
    return (
      <div className="page-container anomaly-page-wrap">
        <FilterBar
          filters={filters}
          setFilters={setFilters}
          filterOptions={filterOptions}
          resetFilters={resetFilters}
        />
        <div className="anomaly-card">
          <p className="text-muted">Loading Anomaly & Fraud Alerts...</p>
        </div>
      </div>
    );
  }

  const criticalCount = anomalyData.severity_breakdown?.CRITICAL || 0;
  const highCount = anomalyData.severity_breakdown?.HIGH || 0;
  const mediumCount = anomalyData.severity_breakdown?.MEDIUM || 0;
  const totalAnomalies = anomalyData.total_anomalies_detected || anomalyData.anomalies?.length || (criticalCount + highCount + mediumCount);

  const critPct = totalAnomalies > 0 ? ((criticalCount / totalAnomalies) * 100).toFixed(1) + "%" : "0%";
  const highPct = totalAnomalies > 0 ? ((highCount / totalAnomalies) * 100).toFixed(1) + "%" : "0%";
  const medPct = totalAnomalies > 0 ? ((mediumCount / totalAnomalies) * 100).toFixed(1) + "%" : "0%";

  return (
    <div className="page-container anomaly-page-wrap">
      {/* GLOBAL DYNAMIC FILTER BAR */}
      <FilterBar
        filters={filters}
        setFilters={setFilters}
        filterOptions={filterOptions}
        resetFilters={resetFilters}
      />

      {/* 1. PAGE HEADER */}
      <div className="anomaly-header-block">
        <h1 className="anomaly-main-title">
          <IconAnomaly size={24} color="#ef4444" /> Anomaly & Fraud Alerts
        </h1>
        <p className="anomaly-main-subtitle">
          Detect unusual sales, margin and inventory activity before it impacts the business.
        </p>
      </div>

      {/* 2. SUMMARY KPI CARDS */}
      <div className="anomaly-kpi-grid">
        <div className="anomaly-kpi-card card-crit">
          <div className="anomaly-kpi-top">
            <span className="anomaly-kpi-label">Critical Alerts</span>
            <span className="badge-danger-soft">Urgent Action</span>
          </div>
          <div className="anomaly-kpi-value text-danger">{criticalCount}</div>
          <span className="anomaly-kpi-subtext">Immediate review required</span>
        </div>

        <div className="anomaly-kpi-card card-high">
          <div className="anomaly-kpi-top">
            <span className="anomaly-kpi-label">High Risk Alerts</span>
            <span className="badge-amber-soft">High Deviation</span>
          </div>
          <div className="anomaly-kpi-value text-amber">{highCount}</div>
          <span className="anomaly-kpi-subtext">Significant statistical outlier</span>
        </div>

        <div className="anomaly-kpi-card card-med">
          <div className="anomaly-kpi-top">
            <span className="anomaly-kpi-label">Medium Alerts</span>
            <span className="badge-blue-soft">Moderate Risk</span>
          </div>
          <div className="anomaly-kpi-value text-primary">{mediumCount}</div>
          <span className="anomaly-kpi-subtext">Moderate variance from mean</span>
        </div>

        <div className="anomaly-kpi-card card-total">
          <div className="anomaly-kpi-top">
            <span className="anomaly-kpi-label">Total Anomalies</span>
            <span className="badge-purple-soft">Flagged</span>
          </div>
          <div className="anomaly-kpi-value text-dark">{totalAnomalies}</div>
          <span className="anomaly-kpi-subtext">
            Out of {anomalyData.total_records_analyzed?.toLocaleString()} transactions
          </span>
        </div>
      </div>

      {/* 3. MAIN ALERT OVERVIEW */}
      <div className="anomaly-card">
        <div className="anomaly-section-header">
          <div>
            <h3 className="anomaly-card-title">Business Alert Overview</h3>
            <p className="anomaly-card-sub">Severity breakdown of flagged transactional and inventory exceptions</p>
          </div>
        </div>

        <div className="anomaly-bar-wrapper">
          <div className="anomaly-bar-track">
            <div
              className="anomaly-bar-fill fill-crit"
              style={{ width: critPct }}
              title={`Critical: ${critPct}`}
            />
            <div
              className="anomaly-bar-fill fill-high"
              style={{ width: highPct }}
              title={`High: ${highPct}`}
            />
            <div
              className="anomaly-bar-fill fill-med"
              style={{ width: medPct }}
              title={`Medium: ${medPct}`}
            />
          </div>

          <div className="anomaly-bar-legend-row">
            <div className="anomaly-legend-item">
              <span className="dot dot-crit" />
              <span className="anomaly-legend-label">Critical Alerts</span>
              <strong className="anomaly-legend-val text-danger">{criticalCount} ({critPct})</strong>
            </div>
            <div className="anomaly-legend-item">
              <span className="dot dot-high" />
              <span className="anomaly-legend-label">High Risk Alerts</span>
              <strong className="anomaly-legend-val text-amber">{highCount} ({highPct})</strong>
            </div>
            <div className="anomaly-legend-item">
              <span className="dot dot-med" />
              <span className="anomaly-legend-label">Medium Alerts</span>
              <strong className="anomaly-legend-val text-primary">{mediumCount} ({medPct})</strong>
            </div>
          </div>
        </div>
      </div>

      {/* 4. PRIORITY ALERTS TABLE (MAIN FOCUS) */}
      {anomalyData.anomalies && anomalyData.anomalies.length > 0 && (
        <div className="anomaly-card">
          <div className="anomaly-section-header">
            <div>
              <h3 className="anomaly-card-title">🚨 Priority Business Alerts</h3>
              <p className="anomaly-card-sub">Detailed audit log of flagged exceptions, revenue anomalies, and inventory risks</p>
            </div>
            <span className="badge-danger-soft">
              {anomalyData.anomalies.length} Flagged Exceptions
            </span>
          </div>

          <div className="table-responsive" style={{ marginTop: "14px" }}>
            <table className="anomaly-action-table">
              <thead>
                <tr>
                  <th>Alert / Record ID</th>
                  <th>Anomaly Type</th>
                  <th>Severity</th>
                  <th>Revenue & Volume</th>
                  <th>Category & Location</th>
                  <th>Business Explanation</th>
                </tr>
              </thead>
              <tbody>
                {anomalyData.anomalies.map((anom) => {
                  let badgeClass = "badge-blue-soft";
                  if (anom.severity === "CRITICAL") badgeClass = "badge-critical";
                  else if (anom.severity === "HIGH") badgeClass = "badge-amber-soft";

                  return (
                    <tr key={anom.invoice_id}>
                      <td>
                        <span className="anomaly-id-pill">#{anom.invoice_id}</span>
                      </td>
                      <td>
                        <strong className="anomaly-type-text">{anom.anomaly_type}</strong>
                      </td>
                      <td>
                        <span className={badgeClass}>{anom.severity}</span>
                      </td>
                      <td>
                        <div className="font-semibold text-main">
                          ₹{anom.metrics.revenue?.toLocaleString()}
                        </div>
                        <div className="text-muted text-xs">
                          {anom.metrics.units} units • Margin: {anom.metrics.margin_pct}%
                        </div>
                      </td>
                      <td>
                        <div className="font-semibold text-main">{anom.brand} ({anom.category})</div>
                        <div className="text-muted text-xs">{anom.city} • {anom.store_format}</div>
                      </td>
                      <td style={{ maxWidth: "380px" }}>
                        <div className="anomaly-reason-text">{anom.reason}</div>
                        <div className="text-muted text-xs" style={{ marginTop: "3px" }}>
                          Z-Score: <strong>+{anom.max_z_score}</strong>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* 6. SECONDARY TECHNICAL DETAILS (DE-EMPHASIZED AT BOTTOM) */}
      <div className="anomaly-card anomaly-tech-panel">
        <h4 className="anomaly-tech-title">⚙️ Anomaly Detection Model Architecture</h4>
        <div className="anomaly-tech-grid">
          <div className="anomaly-tech-item">
            <span className="tech-label">Detection Algorithm</span>
            <span className="tech-val">Multivariate Isolation Forest & Z-Score Analysis</span>
          </div>
          <div className="anomaly-tech-item">
            <span className="tech-label">Total Scope Analyzed</span>
            <span className="tech-val">{anomalyData.total_records_analyzed?.toLocaleString()} Invoices</span>
          </div>
          <div className="anomaly-tech-item">
            <span className="tech-label">Statistical Threshold</span>
            <span className="tech-val">|Z-Score| &gt; 2.5 Baseline Variance</span>
          </div>
          <div className="anomaly-tech-item">
            <span className="tech-label">Engine Status</span>
            <span className="tech-val text-emerald font-semibold">Active Real-Time Monitoring</span>
          </div>
        </div>
      </div>
    </div>
  );
}
