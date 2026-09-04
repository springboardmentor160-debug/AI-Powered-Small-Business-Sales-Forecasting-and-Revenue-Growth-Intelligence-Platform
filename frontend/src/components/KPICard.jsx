import React from 'react';

export default function KPICard({ title, value, icon: Icon, color, subtitle }) {
  return (
    <div className="kpi-card">
      <div className="kpi-header">
        <span className="kpi-title">{title}</span>
        <div className="kpi-icon" style={{ backgroundColor: `${color}20`, color: color }}>
          {Icon && <Icon size={20} />}
        </div>
      </div>
      <div className="kpi-value">{value}</div>
      {subtitle && <div className="kpi-footer">{subtitle}</div>}
    </div>
  );
}
