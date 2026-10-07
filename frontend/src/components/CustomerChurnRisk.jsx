import React, { useState, useEffect } from 'react';
import { getChurnIntelligence } from '../api';

export default function CustomerChurnRisk() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchChurn() {
      try {
        setLoading(true);
        setError(null);
        const result = await getChurnIntelligence();
        setData(result);
      } catch (err) {
        setError(err.message || 'Failed to load churn intelligence.');
      } finally {
        setLoading(false);
      }
    }
    fetchChurn();
  }, []);

  const getRiskBadge = (risk) => {
    switch (risk) {
      case 'High Risk':
        return { label: '⚠️ High Risk', class: 'status-pill status-alert' };
      case 'Medium Risk':
        return { label: '⚡ Medium Risk', class: 'status-pill status-warning' };
      case 'Low Risk':
        return { label: '🛡️ Low Risk', class: 'status-pill status-ok' };
      default:
        return { label: risk, class: 'status-pill status-ok' };
    }
  };

  const getSegmentBadgeClass = (segment) => {
    switch (segment) {
      case 'VIP / Loyal Customers':
        return 'badge-emerald';
      case 'Regular Customers':
        return 'badge-indigo';
      case 'Occasional Shoppers':
        return 'badge-blue';
      case 'At-Risk / Fading Customers':
        return 'badge-amber';
      default:
        return 'badge-indigo';
    }
  };

  return (
    <div className="glass-card" style={{ marginBottom: '32px' }}>
      <div className="card-header">
        <div className="card-title">
          <span>📉</span>
          <div>
            <span style={{ fontSize: '1.05rem', fontWeight: 700 }}>Customer Churn Risk & Retention Intelligence</span>
            <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
              Comparative Machine Learning Classification (Logistic Regression, Random Forest, XGBoost)
            </div>
          </div>
        </div>
        <span className="status-pill status-warning">
          Selected Model: {data?.selected_model || 'Evaluating...'}
        </span>
      </div>

      <div className="card-body">
        {loading ? (
          <div className="loading-spinner" style={{ padding: '24px' }}>
            <div className="spinner"></div>
            <span>Evaluating churn models & customer cohort probabilities...</span>
          </div>
        ) : error ? (
          <div className="msg-banner msg-error">
            <span>⚠️ {error}</span>
          </div>
        ) : (
          <div>
            {/* Top Row: Model Selection & Strategy Banner */}
            <div
              style={{
                background: 'rgba(99, 102, 241, 0.08)',
                border: '1px solid rgba(99, 102, 241, 0.25)',
                borderRadius: 'var(--radius-md)',
                padding: '14px 18px',
                marginBottom: '20px',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                flexWrap: 'wrap',
                gap: '12px',
              }}
            >
              <div>
                <div style={{ fontWeight: 700, fontSize: '0.9rem', color: '#c7d2fe', marginBottom: '4px' }}>
                  🎯 Model Selection Rationale: Prioritizing Recall
                </div>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-main)', maxWidth: '720px' }}>
                  {data?.selection_reason}
                </div>
              </div>
              <div style={{ fontSize: '0.74rem', color: 'var(--text-dim)', textAlign: 'right' }}>
                <div>High Risk Threshold: &ge; {(data?.risk_thresholds?.high * 100).toFixed(0)}%</div>
                <div>Medium Risk Threshold: &ge; {(data?.risk_thresholds?.medium * 100).toFixed(0)}%</div>
              </div>
            </div>

            {/* Model Comparison Table */}
            <div style={{ marginBottom: '24px' }}>
              <h4 style={{ fontSize: '0.9rem', fontWeight: 700, color: 'var(--text-main)', marginBottom: '8px' }}>
                ⚖️ Real Multi-Model Classification Evaluation (Test Set)
              </h4>
              <div className="table-container">
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Classifier Model</th>
                      <th>Precision</th>
                      <th>Recall (Target Priority)</th>
                      <th>F1-Score</th>
                      <th>Accuracy</th>
                      <th>Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {(data?.model_evaluations || []).map((m, idx) => {
                      const isSelected = m.model === data?.selected_model;
                      return (
                        <tr key={idx} style={{ background: isSelected ? 'rgba(99, 102, 241, 0.1)' : 'transparent' }}>
                          <td style={{ fontWeight: 700, color: isSelected ? '#a5b4fc' : 'var(--text-main)' }}>
                            {isSelected ? '⭐ ' : ''}{m.model}
                          </td>
                          <td>{(m.precision * 100).toFixed(1)}%</td>
                          <td style={{ fontWeight: 700, color: '#38bdf8' }}>{(m.recall * 100).toFixed(1)}%</td>
                          <td style={{ fontWeight: 700, color: '#10b981' }}>{m.f1_score.toFixed(4)}</td>
                          <td>{(m.accuracy * 100).toFixed(1)}%</td>
                          <td>
                            <span
                              style={{
                                fontSize: '0.72rem',
                                padding: '2px 8px',
                                borderRadius: '4px',
                                background: isSelected ? 'rgba(16, 185, 129, 0.2)' : 'rgba(255, 255, 255, 0.05)',
                                color: isSelected ? '#34d399' : 'var(--text-muted)',
                                fontWeight: 600,
                              }}
                            >
                              {isSelected ? 'Active Model' : 'Evaluated'}
                            </span>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Customer Cohort Risk Table */}
            <div style={{ marginBottom: '24px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                <h4 style={{ fontSize: '0.9rem', fontWeight: 700, color: 'var(--text-main)' }}>
                  👥 Customer Retention Risk Profiles ({data?.total_customers || 0} Accounts)
                </h4>
                <span style={{ fontSize: '0.74rem', color: 'var(--text-dim)' }}>
                  * Churn probability indicates attrition likelihood; it does not guarantee customer departure.
                </span>
              </div>
              <div className="table-container">
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Customer ID</th>
                      <th>Segment</th>
                      <th>Total Spend</th>
                      <th>Orders</th>
                      <th>Recency (Inactive Days)</th>
                      <th>Churn Probability</th>
                      <th>Retention Risk Category</th>
                    </tr>
                  </thead>
                  <tbody>
                    {(data?.customer_cohort || []).map((c, idx) => {
                      const riskInfo = getRiskBadge(c.retention_risk);
                      const probPct = Math.round(c.churn_probability * 100);
                      return (
                        <tr key={idx}>
                          <td style={{ fontWeight: 700, fontFamily: 'monospace', color: '#38bdf8' }}>
                            {c.customer_id}
                          </td>
                          <td>
                            <span className={`segment-badge ${getSegmentBadgeClass(c.segment)}`}>
                              {c.segment}
                            </span>
                          </td>
                          <td style={{ fontWeight: 700, color: '#10b981' }}>
                            ₹{c.purchase_value.toFixed(2)}
                          </td>
                          <td>{c.purchase_frequency} orders</td>
                          <td>{c.days_since_last_order} days</td>
                          <td style={{ width: '180px' }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                              <div
                                style={{
                                  flex: 1,
                                  height: '8px',
                                  background: 'rgba(255, 255, 255, 0.1)',
                                  borderRadius: '4px',
                                  overflow: 'hidden',
                                }}
                              >
                                <div
                                  style={{
                                    height: '100%',
                                    width: `${probPct}%`,
                                    background:
                                      c.retention_risk === 'High Risk'
                                        ? '#ef4444'
                                        : c.retention_risk === 'Medium Risk'
                                        ? '#f59e0b'
                                        : '#10b981',
                                  }}
                                ></div>
                              </div>
                              <span style={{ fontSize: '0.78rem', fontWeight: 700, minWidth: '35px' }}>
                                {probPct}%
                              </span>
                            </div>
                          </td>
                          <td>
                            <span className={riskInfo.class}>{riskInfo.label}</span>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Segment vs Churn Risk Cross-Tabulation */}
            <div>
              <h4 style={{ fontSize: '0.9rem', fontWeight: 700, color: 'var(--text-main)', marginBottom: '8px' }}>
                🔗 Segment & Churn Retention Cross-Analysis
              </h4>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '12px' }}>
                {(data?.segment_churn_relationship || []).map((segRel, idx) => (
                  <div
                    key={idx}
                    style={{
                      background: 'rgba(255, 255, 255, 0.02)',
                      border: '1px solid var(--border-subtle)',
                      borderRadius: 'var(--radius-sm)',
                      padding: '12px',
                    }}
                  >
                    <div style={{ fontWeight: 600, fontSize: '0.85rem', color: 'var(--text-main)', marginBottom: '4px' }}>
                      {segRel.segment}
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.76rem', color: 'var(--text-muted)' }}>
                      <span>Risk Level:</span>
                      <strong>{segRel.retention_risk}</strong>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.76rem', color: 'var(--text-muted)' }}>
                      <span>Avg Attrition Prob:</span>
                      <strong>{(segRel.avg_churn_prob * 100).toFixed(1)}%</strong>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.76rem', color: 'var(--text-muted)' }}>
                      <span>Cohort Size:</span>
                      <strong>{segRel.customer_count} account(s)</strong>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
