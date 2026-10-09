import React from "react";
import { IconUser, IconSettings } from "../components/Icons";

export default function SettingsPage({
  currentUsername,
  userRole,
  canViewRevenue,
  canViewMargin,
  canViewLowStock,
  canViewForecast,
}) {
  const permissions = [
    { label: "View Revenue Metrics", granted: canViewRevenue },
    { label: "View Margin Metrics", granted: canViewMargin },
    { label: "View Low Stock & Reorders", granted: canViewLowStock },
    { label: "Sales Forecasting & Reports", granted: canViewForecast },
  ];

  return (
    <div className="page-container stg-page-wrap">
      {/* 1. PAGE HEADER */}
      <div className="stg-header-block">
        <h1 className="stg-main-title">
          <IconSettings size={24} color="#64748b" /> System Settings
        </h1>
        <p className="stg-main-subtitle">
          Account details, active role privileges, and platform diagnostics.
        </p>
      </div>

      {/* 2. TWO COLUMN LAYOUT */}
      <div className="stg-grid-2col">
        {/* USER PROFILE */}
        <div className="stg-card">
          <div className="stg-section-header">
            <h3 className="stg-card-title">Active User Account</h3>
            <div className="user-avatar" style={{ width: "32px", height: "32px" }}>
              <IconUser size={16} color="#0f172a" />
            </div>
          </div>

          <div className="stg-metric-list">
            <div className="stg-metric-row">
              <span className="stg-metric-label">Username</span>
              <span className="stg-metric-val font-bold">{currentUsername || "User"}</span>
            </div>
            <div className="stg-metric-row">
              <span className="stg-metric-label">Assigned Role</span>
              <span className="badge-teal">{userRole || "Member"}</span>
            </div>
            <div className="stg-metric-row">
              <span className="stg-metric-label">Auth Token</span>
              <span className="badge-blue">JWT Active</span>
            </div>
            <div className="stg-metric-row">
              <span className="stg-metric-label">Backend Host</span>
              <span className="stg-metric-val font-bold">http://127.0.0.1:8000</span>
            </div>
            <div className="stg-metric-row">
              <span className="stg-metric-label">Frontend Port</span>
              <span className="stg-metric-val font-bold">http://localhost:5173</span>
            </div>
          </div>
        </div>

        {/* ROLE ACCESS MATRIX */}
        <div className="stg-card">
          <h3 className="stg-card-title">Role Access Matrix</h3>
          <p className="stg-card-sub" style={{ marginBottom: "16px" }}>
            Permission grants for current role: <strong>{userRole || "Member"}</strong>
          </p>
          <div className="stg-metric-list">
            {permissions.map((p) => (
              <div className="stg-metric-row" key={p.label}>
                <span className="stg-metric-label">{p.label}</span>
                <span className={p.granted ? "badge-teal" : "badge-critical"}>
                  {p.granted ? "Granted" : "Restricted"}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* 3. PLATFORM INFO */}
      <div className="stg-card">
        <h3 className="stg-card-title">⚙️ Platform Diagnostics</h3>
        <p className="stg-card-sub" style={{ marginBottom: "16px" }}>
          Technical stack and engine status
        </p>
        <div className="stg-tech-grid">
          {[
            { label: "Backend Framework", val: "FastAPI (Python 3.13)" },
            { label: "ML Engine", val: "scikit-learn · XGBoost · Prophet" },
            { label: "Frontend Framework", val: "React 18 + Vite" },
            { label: "Auth Method", val: "JWT (HS256, 60min expiry)" },
            { label: "Data Source", val: "FMCG Retail Dataset (CSV)" },
            { label: "Engine Status", val: "Active — Port 8000" },
          ].map((item) => (
            <div className="stg-tech-item" key={item.label}>
              <span className="stg-tech-label">{item.label}</span>
              <span className="stg-tech-val">{item.val}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
