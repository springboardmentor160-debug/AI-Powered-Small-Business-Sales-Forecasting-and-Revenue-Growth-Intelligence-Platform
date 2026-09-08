import React from 'react';

export default function KPICard({ label, value, subtext, icon, accent = '#6366f1' }) {
  return (
    <div className="glass-card kpi-card" style={{ '--accent-color': accent }}>
      <div className="kpi-header">
        <span className="kpi-label">{label}</span>
        <div className="kpi-icon">{icon}</div>
      </div>
      <div className="kpi-value">{value}</div>
      {subtext && <div className="kpi-subtext">{subtext}</div>}
    </div>
  );
}
