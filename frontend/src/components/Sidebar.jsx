import React, { useState, useEffect } from "react";
import {
  IconDashboard,
  IconSales,
  IconInventory,
  IconCustomers,
  IconInvoices,
  IconAI,
  IconForecasting,
  IconSegmentation,
  IconChurn,
  IconRecommendations,
  IconAnomaly,
  IconReports,
  IconSettings,
  IconChevronDown,
  IconUpload,
} from "./Icons";

export default function Sidebar({ activePage, setActivePage }) {
  const navItems = [
    { id: "dashboard", label: "Dashboard", icon: IconDashboard },
    { id: "sales", label: "Sales", icon: IconSales },
    { id: "inventory", label: "Inventory", icon: IconInventory },
    { id: "customers", label: "Customers", icon: IconCustomers },
    { id: "invoices", label: "Invoices", icon: IconInvoices },
  ];

  const aiSubItems = [
    { id: "forecasting", label: "Forecasting", icon: IconForecasting },
    { id: "segmentation", label: "Segmentation", icon: IconSegmentation },
    { id: "churn", label: "Churn Prediction", icon: IconChurn },
    { id: "recommendations", label: "Recommendations", icon: IconRecommendations },
    { id: "anomalies", label: "Anomaly Detection", icon: IconAnomaly },
  ];
  const visibleAiActive = aiSubItems.some((item) => item.id === activePage);
  const isAiActive = visibleAiActive;

  const [aiExpanded, setAiExpanded] = useState(isAiActive);

  useEffect(() => {
    if (isAiActive) {
      setAiExpanded(true);
    }
  }, [activePage, isAiActive]);

  return (
    <aside className="app-sidebar">
      {/* BRANDING HEADER */}
      <div className="sidebar-brand">
        <div className="brand-logo-icon">
          <IconAI size={22} color="#ffffff" />
        </div>
        <div className="brand-text-group">
          <span className="brand-title">MarketMind AI</span>
          <span className="brand-subtitle">Intelligence Platform</span>
        </div>
      </div>

      {/* NAVIGATION ITEMS */}
      <nav className="sidebar-nav">
        <div className="nav-section-label">MAIN NAVIGATION</div>

        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activePage === item.id;
          return (
            <button
              key={item.id}
              className={`nav-item ${isActive ? "active" : ""}`}
              onClick={() => setActivePage(item.id)}
            >
              <Icon size={19} className="nav-icon" />
              <span className="nav-label">{item.label}</span>
            </button>
          );
        })}

        {/* AI INSIGHTS EXPANDABLE SECTION */}
        {aiSubItems.length > 0 && (
          <div className="nav-group">
            <button
              className={`nav-item nav-item-parent ${isAiActive ? "active-parent" : ""}`}
              onClick={() => setAiExpanded(!aiExpanded)}
            >
              <div className="nav-item-left">
                <IconAI size={19} className="nav-icon ai-glow-icon" />
                <span className="nav-label">AI Insights</span>
              </div>
              <IconChevronDown
                size={16}
                style={{
                  transform: aiExpanded ? "rotate(180deg)" : "rotate(0deg)",
                  transition: "transform 0.2s ease",
                }}
              />
            </button>

            {aiExpanded && (
              <div className="nav-submenu">
                {aiSubItems.map((sub) => {
                  const SubIcon = sub.icon;
                  const isSubActive = activePage === sub.id;
                  return (
                    <button
                      key={sub.id}
                      className={`nav-subitem ${isSubActive ? "active" : ""}`}
                      onClick={() => setActivePage(sub.id)}
                    >
                      <SubIcon size={16} className="nav-subicon" />
                      <span>{sub.label}</span>
                    </button>
                  );
                })}
              </div>
            )}
          </div>
        )}

        <div className="nav-section-label" style={{ marginTop: "24px" }}>
          MANAGEMENT
        </div>

        <button
          className={`nav-item ${activePage === "data-upload" ? "active" : ""}`}
          onClick={() => setActivePage("data-upload")}
        >
          <IconUpload size={19} className="nav-icon" />
          <span className="nav-label">Data Upload</span>
        </button>

        <button
          className={`nav-item ${activePage === "reports" ? "active" : ""}`}
          onClick={() => setActivePage("reports")}
        >
          <IconReports size={19} className="nav-icon" />
          <span className="nav-label">Reports</span>
        </button>

        <button
          className={`nav-item ${activePage === "settings" ? "active" : ""}`}
          onClick={() => setActivePage("settings")}
        >
          <IconSettings size={19} className="nav-icon" />
          <span className="nav-label">Settings</span>
        </button>
      </nav>

      {/* SYSTEM STATUS BADGE */}
      <div className="sidebar-footer">
        <div className="status-indicator">
          <span className="status-dot"></span>
          <span className="status-text">Engine Online (Port 8000)</span>
        </div>
      </div>
    </aside>
  );
}
