import React, { useState, useEffect } from 'react';
import { getAnomalies } from '../api';

export default function AnomalyAlerts() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [reviewedOrders, setReviewedOrders] = useState({});

  useEffect(() => {
    async function fetchAnomalies() {
      try {
        setLoading(true);
        setError(null);
        const result = await getAnomalies();
        setData(result);
      } catch (err) {
        setError(err.message || 'Failed to load anomaly detection alerts.');
      } finally {
        setLoading(false);
      }
    }
    fetchAnomalies();
  }, []);

  const toggleReview = (orderId) => {
    setReviewedOrders((prev) => ({
      ...prev,
      [orderId]: !prev[orderId],
    }));
  };

  const getSeverityBadge = (severity) => {
    switch (severity) {
      case 'High':
        return { label: 'High Priority', class: 'status-pill status-alert' };
      case 'Medium':
        return { label: 'Medium Priority', class: 'status-pill status-warning' };
      default:
        return { label: 'Standard', class: 'status-pill status-ok' };
    }
  };

  return (
    <div className="glass-card" style={{ marginBottom: '32px' }}>
      <div className="card-header">
        <div className="card-title">
          <span>🚨</span>
          <div>
            <span style={{ fontSize: '1.05rem', fontWeight: 700 }}>Sales Anomaly Detection & Review Alerts</span>
            <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
              Statistical Z-Score (|z| &gt; 3.0) & Isolation Forest Multi-Dimensional Outlier Analysis
            </div>
          </div>
        </div>
        <span className="status-pill status-alert">
          {data?.anomalies_detected_count || 0} Flagged for Review
        </span>
      </div>

      <div className="card-body">
        {loading ? (
          <div className="loading-spinner" style={{ padding: '24px' }}>
            <div className="spinner"></div>
            <span>Scanning transaction space for statistical & dimensional outliers...</span>
          </div>
        ) : error ? (
          <div className="msg-banner msg-error">
            <span>⚠️ {error}</span>
          </div>
        ) : (
          <div>
            {/* Notice Banner */}
            <div
              style={{
                background: 'rgba(245, 158, 11, 0.08)',
                border: '1px solid rgba(245, 158, 11, 0.25)',
                borderRadius: 'var(--radius-md)',
                padding: '12px 16px',
                marginBottom: '20px',
                display: 'flex',
                alignItems: 'center',
                gap: '12px',
              }}
            >
              <span style={{ fontSize: '1.4rem' }}>🛡️</span>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-main)' }}>
                <strong>Human-in-the-Loop Verification Protocol:</strong> Anomalies reflect statistically unusual transaction patterns
                (e.g., volume surges or total value deviations) flagged for human review. They are <em>not</em> confirmation of fraud.
              </div>
            </div>

            {/* Method Comparison Summary Card */}
            <div
              style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
                gap: '14px',
                marginBottom: '22px',
              }}
            >
              <div
                style={{
                  background: 'rgba(255, 255, 255, 0.02)',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: 'var(--radius-sm)',
                  padding: '14px',
                }}
              >
                <div style={{ fontSize: '0.82rem', fontWeight: 700, color: '#38bdf8', marginBottom: '4px' }}>
                  📊 Statistical Z-Score (1D Target)
                </div>
                <div style={{ fontSize: '0.76rem', color: 'var(--text-dim)', marginBottom: '8px' }}>
                  Flags revenue totals where |Z| &gt; 3.0 standard deviations from mean ($87.12)
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.82rem' }}>
                  <span>Detected Transactions:</span>
                  <strong>{data?.comparison?.zscore?.detected_count || 0} order(s)</strong>
                </div>
              </div>

              <div
                style={{
                  background: 'rgba(255, 255, 255, 0.02)',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: 'var(--radius-sm)',
                  padding: '14px',
                }}
              >
                <div style={{ fontSize: '0.82rem', fontWeight: 700, color: '#a855f7', marginBottom: '4px' }}>
                  🌲 Isolation Forest (3D Features)
                </div>
                <div style={{ fontSize: '0.76rem', color: 'var(--text-dim)', marginBottom: '8px' }}>
                  Isolates multidimensional combinations across [quantity, unit_price, total_amount]
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.82rem' }}>
                  <span>Detected Outliers:</span>
                  <strong>{data?.comparison?.isolation_forest?.detected_count || 0} order(s) ({data?.comparison?.isolation_forest?.detected_orders?.join(', ') || 'None'})</strong>
                </div>
              </div>
            </div>

            {/* Actionable Alerts List */}
            <div style={{ marginBottom: '24px' }}>
              <h4 style={{ fontSize: '0.9rem', fontWeight: 700, color: 'var(--text-main)', marginBottom: '12px' }}>
                ⚠️ Active Transaction Review Queue ({data?.alerts?.length || 0} Items)
              </h4>

              {data?.alerts && data.alerts.length > 0 ? (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                  {data.alerts.map((alert, idx) => {
                    const isReviewed = reviewedOrders[alert.order_id];
                    const severityInfo = getSeverityBadge(alert.severity);
                    return (
                      <div
                        key={idx}
                        style={{
                          background: isReviewed ? 'rgba(16, 185, 129, 0.05)' : 'rgba(255, 255, 255, 0.03)',
                          border: isReviewed
                            ? '1px solid rgba(16, 185, 129, 0.3)'
                            : '1px solid rgba(239, 68, 68, 0.3)',
                          borderRadius: 'var(--radius-md)',
                          padding: '16px',
                          display: 'flex',
                          justifyContent: 'space-between',
                          alignItems: 'flex-start',
                          flexWrap: 'wrap',
                          gap: '12px',
                        }}
                      >
                        <div style={{ flex: '1 1 450px' }}>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '6px' }}>
                            <span style={{ fontWeight: 800, color: '#38bdf8', fontFamily: 'monospace' }}>
                              Order #{alert.order_id}
                            </span>
                            <span className={severityInfo.class}>{severityInfo.label}</span>
                            <span
                              style={{
                                fontSize: '0.72rem',
                                background: 'rgba(255, 255, 255, 0.05)',
                                padding: '2px 8px',
                                borderRadius: '4px',
                                color: 'var(--text-muted)',
                              }}
                            >
                              Method: {alert.detection_method}
                            </span>
                          </div>

                          <div style={{ fontSize: '0.84rem', color: 'var(--text-main)', marginBottom: '8px' }}>
                            {alert.message}
                          </div>

                          <div style={{ display: 'flex', gap: '16px', fontSize: '0.76rem', color: 'var(--text-dim)', flexWrap: 'wrap' }}>
                            <span>Customer: <strong>{alert.customer_id}</strong></span>
                            <span>Product: <strong>{alert.product_name}</strong></span>
                            <span>Quantity: <strong>{alert.relevant_values?.quantity} units</strong></span>
                            <span>Total Value: <strong style={{ color: '#10b981' }}>₹{alert.relevant_values?.total_amount?.toFixed(2)}</strong></span>
                            <span>Anomaly Score: <strong>{alert.relevant_values?.isolation_forest_score}</strong></span>
                          </div>
                        </div>

                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                          <button
                            onClick={() => toggleReview(alert.order_id)}
                            className="btn btn-secondary"
                            style={{
                              fontSize: '0.78rem',
                              padding: '6px 14px',
                              background: isReviewed ? 'rgba(16, 185, 129, 0.2)' : 'rgba(255, 255, 255, 0.08)',
                              color: isReviewed ? '#34d399' : 'var(--text-main)',
                              border: isReviewed ? '1px solid #10b981' : '1px solid var(--border-subtle)',
                            }}
                          >
                            {isReviewed ? '✓ Verified by Manager' : 'Mark Reviewed'}
                          </button>
                        </div>
                      </div>
                    );
                  })}
                </div>
              ) : (
                <div
                  style={{
                    background: 'rgba(16, 185, 129, 0.05)',
                    border: '1px solid rgba(16, 185, 129, 0.2)',
                    borderRadius: 'var(--radius-sm)',
                    padding: '16px',
                    textAlign: 'center',
                    fontSize: '0.84rem',
                    color: '#34d399',
                  }}
                >
                  ✓ All transactions within standard expected distributions. No review alerts pending.
                </div>
              )}
            </div>

            {/* Inventory Anomaly Assessment Documentation Card */}
            <div
              style={{
                background: 'rgba(255, 255, 255, 0.02)',
                border: '1px solid var(--border-subtle)',
                borderRadius: 'var(--radius-sm)',
                padding: '14px 16px',
                fontSize: '0.78rem',
                color: 'var(--text-muted)',
              }}
            >
              <div style={{ fontWeight: 700, color: 'var(--text-main)', marginBottom: '4px' }}>
                📦 Inventory Movement Anomaly Assessment
              </div>
              <div>{data?.inventory_anomalies?.message}</div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
