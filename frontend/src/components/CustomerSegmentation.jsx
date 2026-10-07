import React, { useEffect, useState } from "react";
import { getSegmentationSummary, getSegmentationCustomers, getSegments } from "../api";

export default function CustomerSegmentation() {
  const [summary, setSummary] = useState(null);
  const [customers, setCustomers] = useState([]);
  const [segmentsAgg, setSegmentsAgg] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchData() {
      try {
        setLoading(true);
        const [sumData, custData, segsData] = await Promise.all([
          getSegmentationSummary().catch(() => null),
          getSegmentationCustomers().catch(() => []),
          getSegments().catch(() => []),
        ]);
        setSummary(sumData || null);
        setCustomers(Array.isArray(custData) ? custData : []);
        setSegmentsAgg(Array.isArray(segsData) ? segsData : []);
      } catch (err) {
        setError(err.message || "Failed to load customer segmentation data.");
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="glass-card" style={{ marginBottom: "32px", padding: "32px", textAlign: "center" }}>
        <div className="loading-spinner">
          <div className="spinner"></div>
          <span>Loading Customer Segmentation Intelligence...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="msg-banner msg-error" style={{ marginBottom: "32px" }}>
        <span>⚠️ Segmentation Notice: {error}</span>
      </div>
    );
  }

  const getSegmentBadgeClass = (segmentName) => {
    if (!segmentName) return "segment-default";
    if (segmentName.includes("VIP") || segmentName.includes("Loyal")) {
      return "segment-vip";
    }
    if (segmentName.includes("Regular")) {
      return "segment-regular";
    }
    if (segmentName.includes("Occasional")) {
      return "segment-occasional";
    }
    if (segmentName.includes("At-Risk") || segmentName.includes("Fading")) {
      return "segment-atrisk";
    }
    return "segment-default";
  };

  const safeSegments = Array.isArray(segmentsAgg) ? segmentsAgg : [];
  const maxCustCount = Math.max(...safeSegments.map((s) => s?.customer_count || 0), 1);
  const totalCustomers = summary?.total_customers || customers?.length || 0;

  return (
    <div className="glass-card" style={{ marginBottom: "32px" }}>
      {/* Header */}
      <div className="card-header" style={{ flexWrap: "wrap", gap: "12px" }}>
        <div>
          <div className="card-title">
            <span>🎯</span>
            <span>Customer Segments & Behavioral Intelligence</span>
          </div>
          <p style={{ fontSize: "0.82rem", color: "var(--text-muted)", marginTop: "3px" }}>
            K-Means (K=4) & Hierarchical Clustering with Aggregated Performance Metrics
          </p>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: "10px", flexWrap: "wrap" }}>
          <span className="info-tag">
            👥 {totalCustomers} Total Customers
          </span>
          <span className="info-tag" style={{ background: "rgba(16, 185, 129, 0.15)", color: "#34d399", borderColor: "rgba(16, 185, 129, 0.3)" }}>
            ⚡ 4 ML Clusters Active
          </span>
        </div>
      </div>

      <div className="card-body">
        {/* Top Section: Segment KPI Cards & Real-Time Distribution */}
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))", gap: "24px", marginBottom: "32px" }}>
          {/* Left: 4 Segment Metric Cards */}
          <div style={{ gridColumn: "span 2", display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: "14px" }}>
            {summary?.segments?.map((seg, idx) => {
              const segPct = Math.round(((seg?.customer_count || 0) / (totalCustomers || 1)) * 100);
              return (
                <div key={idx} className="segment-card">
                  <div>
                    <div className="segment-card-header">
                      <span className={`segment-badge ${getSegmentBadgeClass(seg?.segment)}`}>
                        {seg?.segment}
                      </span>
                      <span style={{ fontSize: "0.74rem", color: "var(--text-dim)", fontFamily: "monospace" }}>
                        {segPct}% of total
                      </span>
                    </div>
                    <div style={{ fontSize: "1.75rem", fontWeight: 800, color: "var(--text-main)", lineHeight: 1.1 }}>
                      {seg?.customer_count || 0}{" "}
                      <span style={{ fontSize: "0.78rem", fontWeight: 500, color: "var(--text-muted)" }}>customers</span>
                    </div>
                  </div>

                  <div className="segment-card-stats">
                    <div className="segment-stat-row">
                      <span>Avg Spend:</span>
                      <strong>₹{Number(seg?.avg_purchase_value || 0).toFixed(2)}</strong>
                    </div>
                    <div className="segment-stat-row">
                      <span>Avg Frequency:</span>
                      <strong>{Number(seg?.avg_purchase_frequency || 0).toFixed(1)} orders</strong>
                    </div>
                    <div className="segment-stat-row">
                      <span>Activity Span:</span>
                      <strong>{Number(seg?.avg_activity_days || 0).toFixed(0)} days</strong>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Right: Distribution Bars Breakdown */}
          <div className="segment-card" style={{ display: "flex", flexDirection: "column", justifyContent: "space-between" }}>
            <div>
              <h4 style={{ fontSize: "0.95rem", fontWeight: 700, color: "var(--text-main)", marginBottom: "4px" }}>
                📊 Segment Distribution
              </h4>
              <p style={{ fontSize: "0.76rem", color: "var(--text-muted)", marginBottom: "16px" }}>
                Real-time cohort density from ML cluster assignments
              </p>

              <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
                {safeSegments.map((seg, idx) => {
                  const pct = Math.round(((seg?.customer_count || 0) / maxCustCount) * 100);
                  return (
                    <div key={idx} className="dist-bar-item">
                      <div className="dist-bar-header">
                        <span style={{ fontWeight: 600 }}>{seg?.segment || "Unknown"}</span>
                        <span>
                          <strong>{seg?.customer_count || 0}</strong> cust (₹{seg?.avg_purchase_value || 0})
                        </span>
                      </div>
                      <div className="dist-bar-track">
                        <div className="dist-bar-fill" style={{ width: `${Math.max(pct, 12)}%` }}></div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            <div style={{ marginTop: "16px", paddingTop: "12px", borderTop: "1px solid var(--border-subtle)", fontSize: "0.74rem", color: "var(--text-dim)", textAlign: "center" }}>
              Clustered via K-Means & Agglomerative Hierarchical Models
            </div>
          </div>
        </div>

        {/* Customer Profiles Data Table */}
        <div>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "14px" }}>
            <h4 style={{ fontSize: "0.95rem", fontWeight: 700, color: "var(--text-main)" }}>
              👤 Individual Customer Behavioral Profiles ({customers.length} Records)
            </h4>
            <span style={{ fontSize: "0.76rem", color: "var(--text-muted)" }}>
              Sorted by Recency & Frequency
            </span>
          </div>

          <div className="table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Customer ID</th>
                  <th>Order Frequency</th>
                  <th>Total Spent</th>
                  <th>Activity Span</th>
                  <th>K-Means Cluster</th>
                  <th>Hierarchical Cluster</th>
                  <th>Assigned Segment</th>
                </tr>
              </thead>
              <tbody>
                {(customers || []).map((c, i) => (
                  <tr key={i}>
                    <td style={{ fontWeight: 700, color: "#38bdf8", fontFamily: "monospace" }}>
                      {c?.customer_id}
                    </td>
                    <td>{c?.purchase_frequency} orders</td>
                    <td style={{ fontWeight: 700, color: "#10b981" }}>
                      ₹{Number(c?.purchase_value || 0).toFixed(2)}
                    </td>
                    <td>{c?.customer_activity_days} days</td>
                    <td>
                      <span className="info-tag" style={{ fontFamily: "monospace" }}>
                        Cluster {c?.cluster}
                      </span>
                    </td>
                    <td>
                      <span className="info-tag" style={{ fontFamily: "monospace" }}>
                        Cluster {c?.cluster_hierarchical}
                      </span>
                    </td>
                    <td>
                      <span className={`segment-badge ${getSegmentBadgeClass(c?.segment)}`}>
                        {c?.segment}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
