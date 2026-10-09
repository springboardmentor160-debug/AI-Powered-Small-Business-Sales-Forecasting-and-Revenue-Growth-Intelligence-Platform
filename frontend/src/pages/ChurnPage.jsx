import React from "react";
import FilterBar from "../components/FilterBar";
import { IconChurn } from "../components/Icons";

export default function ChurnPage({
  filters,
  setFilters,
  filterOptions,
  resetFilters,
  churnData,
}) {
  if (!churnData) {
    return (
      <div className="page-container churn-page-wrap">
        <FilterBar
          filters={filters}
          setFilters={setFilters}
          filterOptions={filterOptions}
          resetFilters={resetFilters}
        />
        <div className="churn-card">
          <p className="text-muted">Loading Churn Risk Intelligence...</p>
        </div>
      </div>
    );
  }

  const highRiskObj = churnData.risk_distribution?.["High Risk"] || { count: 0, percentage: "0%" };
  const medRiskObj = churnData.risk_distribution?.["Medium Risk"] || { count: 0, percentage: "0%" };
  const lowRiskObj = churnData.risk_distribution?.["Low Risk"] || { count: 0, percentage: "0%" };

  return (
    <div className="page-container churn-page-wrap">
      {/* GLOBAL DYNAMIC FILTER BAR */}
      <FilterBar
        filters={filters}
        setFilters={setFilters}
        filterOptions={filterOptions}
        resetFilters={resetFilters}
      />

      {/* 1. PAGE HEADER */}
      <div className="churn-header-block">
        <h1 className="churn-main-title">
          <IconChurn size={24} color="#ef4444" /> Customer Churn Risk
        </h1>
        <p className="churn-main-subtitle">
          Identify customers at risk and take action before they leave.
        </p>
      </div>

      {/* 2. SUMMARY KPI CARDS */}
      <div className="churn-kpi-grid">
        <div className="churn-kpi-card card-high">
          <div className="churn-kpi-top">
            <span className="churn-kpi-label">High Risk Customers</span>
            <span className="badge-danger-soft">≥ 70% Risk</span>
          </div>
          <div className="churn-kpi-value text-danger">
            {highRiskObj.count?.toLocaleString()}
          </div>
          <span className="churn-kpi-subtext">
            {highRiskObj.percentage} of customer base
          </span>
        </div>

        <div className="churn-kpi-card card-med">
          <div className="churn-kpi-top">
            <span className="churn-kpi-label">Medium Risk Customers</span>
            <span className="badge-amber-soft">40% - 69%</span>
          </div>
          <div className="churn-kpi-value text-amber">
            {medRiskObj.count?.toLocaleString()}
          </div>
          <span className="churn-kpi-subtext">
            {medRiskObj.percentage} of customer base
          </span>
        </div>

        <div className="churn-kpi-card card-low">
          <div className="churn-kpi-top">
            <span className="churn-kpi-label">Low Risk Customers</span>
            <span className="badge-green-soft">&lt; 40%</span>
          </div>
          <div className="churn-kpi-value text-emerald">
            {lowRiskObj.count?.toLocaleString()}
          </div>
          <span className="churn-kpi-subtext">
            {lowRiskObj.percentage} of customer base
          </span>
        </div>

        <div className="churn-kpi-card card-overall">
          <div className="churn-kpi-top">
            <span className="churn-kpi-label">Overall Churn Risk</span>
            <span className="badge-blue-soft">Threshold</span>
          </div>
          <div className="churn-kpi-value text-primary">
            {churnData.overall_churn_rate_pct}
          </div>
          <span className="churn-kpi-subtext">Inactivity ≥ 90 days</span>
        </div>
      </div>

      {/* 3. MAIN INSIGHT CARD: RETENTION RISK OVERVIEW */}
      <div className="churn-card">
        <div className="churn-section-header">
          <div>
            <h3 className="churn-card-title">Retention Risk Overview</h3>
            <p className="churn-card-sub">Distribution of customer churn risk across active accounts</p>
          </div>
          {churnData.selected_best_model && (
            <span className="churn-engine-tag">
              Model Engine: {churnData.selected_best_model}
            </span>
          )}
        </div>

        <div className="churn-bar-wrapper">
          <div className="churn-bar-track">
            <div
              className="churn-bar-fill fill-high"
              style={{ width: highRiskObj.percentage }}
              title={`High Risk: ${highRiskObj.percentage}`}
            />
            <div
              className="churn-bar-fill fill-med"
              style={{ width: medRiskObj.percentage }}
              title={`Medium Risk: ${medRiskObj.percentage}`}
            />
            <div
              className="churn-bar-fill fill-low"
              style={{ width: lowRiskObj.percentage }}
              title={`Low Risk: ${lowRiskObj.percentage}`}
            />
          </div>

          <div className="churn-bar-legend-row">
            <div className="churn-legend-item">
              <span className="dot dot-high" />
              <span className="churn-legend-label">High Risk (≥70%)</span>
              <strong className="churn-legend-val text-danger">{highRiskObj.percentage} ({highRiskObj.count?.toLocaleString()})</strong>
            </div>
            <div className="churn-legend-item">
              <span className="dot dot-med" />
              <span className="churn-legend-label">Medium Risk (40%-69%)</span>
              <strong className="churn-legend-val text-amber">{medRiskObj.percentage} ({medRiskObj.count?.toLocaleString()})</strong>
            </div>
            <div className="churn-legend-item">
              <span className="dot dot-low" />
              <span className="churn-legend-label">Low Risk (&lt;40%)</span>
              <strong className="churn-legend-val text-emerald">{lowRiskObj.percentage} ({lowRiskObj.count?.toLocaleString()})</strong>
            </div>
          </div>
        </div>
      </div>

      {/* 4. MAIN ACTIONABLE SECTION: HIGH RISK CUSTOMER RECORDS */}
      {churnData.sample_high_risk_invoices && churnData.sample_high_risk_invoices.length > 0 && (
        <div className="churn-card">
          <div className="churn-section-header">
            <div>
              <h3 className="churn-card-title">🚨 High Risk Customer Action List</h3>
              <p className="churn-card-sub">Priority accounts requiring immediate retention intervention</p>
            </div>
            <span className="badge-danger-soft">
              {churnData.sample_high_risk_invoices.length} High Risk Accounts
            </span>
          </div>

          <div className="table-responsive" style={{ marginTop: "14px" }}>
            <table className="churn-action-table">
              <thead>
                <tr>
                  <th>Invoice / Record ID</th>
                  <th>Cohort Segment</th>
                  <th>Inactivity</th>
                  <th>Churn Risk</th>
                  <th>Risk Tier</th>
                  <th>Location & Product Category</th>
                </tr>
              </thead>
              <tbody>
                {churnData.sample_high_risk_invoices.map((inv) => (
                  <tr key={inv.invoice_id}>
                    <td>
                      <span className="churn-id-pill">#{inv.invoice_id}</span>
                    </td>
                    <td>
                      <strong className="churn-cohort-name">{inv.segment_name}</strong>
                    </td>
                    <td>
                      <span className="text-amber font-semibold">{inv.inactivity_days} days inactive</span>
                    </td>
                    <td>
                      <span className="churn-prob-badge">{inv.churn_risk_pct}</span>
                    </td>
                    <td>
                      <span className="badge-critical">HIGH RISK</span>
                    </td>
                    <td className="text-muted text-sm">
                      {inv.city} • {inv.store_format} ({inv.brand} - {inv.category})
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* 5. SECONDARY ANALYTICS: COHORT RISK & CHANNEL RISK */}
      <div className="churn-grid-2col">
        {/* Cohort Linkage */}
        {churnData.churn_risk_by_segment_cohort && (
          <div className="churn-card">
            <h3 className="churn-card-title">👥 Risk Breakdown by Customer Cohort</h3>
            <p className="churn-card-sub">Segment risk profiling and high-risk cohort proportions</p>
            <div className="table-responsive" style={{ marginTop: "14px" }}>
              <table className="churn-mini-table">
                <thead>
                  <tr>
                    <th>Cohort Name</th>
                    <th>Mean Risk</th>
                    <th>High Risk Count</th>
                    <th>High Risk %</th>
                  </tr>
                </thead>
                <tbody>
                  {churnData.churn_risk_by_segment_cohort.map((cohort) => (
                    <tr key={cohort.cluster_id}>
                      <td><strong>{cohort.segment_name}</strong></td>
                      <td>{cohort.mean_churn_probability_pct}</td>
                      <td className="text-danger font-semibold">{cohort.high_risk_count?.toLocaleString()}</td>
                      <td>
                        <span className="badge-danger-soft">{cohort.high_risk_pct}</span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Store & Category Risk */}
        <div className="churn-card">
          <h3 className="churn-card-title">🏬 Channel & Category Risk Profiles</h3>
          <p className="churn-card-sub">Risk concentration across store formats and categories</p>
          <div className="churn-tags-section">
            <span className="churn-subheading">STORE FORMAT RISK</span>
            <div className="churn-chips-grid">
              {Object.entries(churnData.churn_risk_by_store_format || {}).map(([fmt, rate]) => (
                <div className="churn-chip" key={fmt}>
                  <span className="chip-key">{fmt}</span>
                  <strong className="chip-val text-danger">{rate}</strong>
                </div>
              ))}
            </div>

            <span className="churn-subheading" style={{ marginTop: "16px" }}>PRODUCT CATEGORY RISK</span>
            <div className="churn-chips-grid">
              {Object.entries(churnData.churn_risk_by_category || {}).map(([cat, rate]) => (
                <div className="churn-chip" key={cat}>
                  <span className="chip-key">{cat}</span>
                  <strong className="chip-val text-amber">{rate}</strong>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* 6. TECHNICAL DETAILS (DE-EMPHASIZED) */}
      <div className="churn-grid-2col">
        {/* Key Risk Drivers */}
        <div className="churn-card">
          <h3 className="churn-card-title">📊 Key Churn Risk Drivers</h3>
          <p className="churn-card-sub">Top factors influencing risk score calculation</p>
          <div className="churn-feature-list" style={{ marginTop: "14px" }}>
            {(churnData.feature_importance || []).map((item, idx) => (
              <div className="churn-feature-row" key={idx}>
                <span className="churn-feature-name">{item.feature}</span>
                <span className="churn-feature-val text-emerald font-semibold">
                  {item.importance !== undefined ? item.importance : item.coefficient} ({item.impact})
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Model Evaluation Benchmark */}
        {churnData.model_comparisons && (
          <div className="churn-card">
            <div className="churn-section-header">
              <div>
                <h3 className="churn-card-title">🤖 Model Evaluation Benchmark</h3>
                <p className="churn-card-sub">Stratified test set evaluation performance</p>
              </div>
            </div>
            <div className="table-responsive" style={{ marginTop: "14px" }}>
              <table className="churn-mini-table">
                <thead>
                  <tr>
                    <th>Model</th>
                    <th>Accuracy</th>
                    <th>Recall</th>
                    <th>F1</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {churnData.model_comparisons.map((m) => {
                    const isBest = m.model_name === churnData.selected_best_model;
                    return (
                      <tr key={m.model_name} className={isBest ? "row-selected" : ""}>
                        <td><strong>{m.model_name}</strong></td>
                        <td>{m.accuracy_pct}</td>
                        <td className="font-bold text-primary">{m.recall_pct}</td>
                        <td>{m.f1_score}</td>
                        <td>
                          {isBest ? (
                            <span className="badge-teal">Selected Best</span>
                          ) : (
                            <span className="text-muted text-xs">Evaluated</span>
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
      </div>

      {/* DE-EMPHASIZED NOTES FOOTER */}
      {(churnData.limitation_note || churnData.selection_reason) && (
        <div className="churn-notes-footer">
          {churnData.limitation_note && (
            <div className="churn-note-chip">
              ℹ️ <strong>Dataset Context:</strong> {churnData.limitation_note}
            </div>
          )}
          {churnData.selection_reason && (
            <div className="churn-note-chip">
              💡 <strong>Model Selection Rationale:</strong> {churnData.selection_reason}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
