import React from "react";
import { IconUser, IconLogout, IconReports } from "./Icons";

export default function Header({
  activePage,
  currentUsername,
  userRole,
  handleLogout,
  canViewForecast,
  handleDownloadReport,
  isDownloadingReport,
  activeDatasetId,
  activeDatasetFilename,
}) {
  const getPageMeta = (page) => {
    switch (page) {
      case "dashboard":
        return { title: "Dashboard", category: "Overview" };
      case "sales":
        return { title: "Sales Analytics", category: "Revenue & Trends" };
      case "inventory":
        return { title: "Inventory Intelligence", category: "Stock & Reorders" };
      case "customers":
        return { title: "Customer Intelligence", category: "Cohorts & Loyalty" };
      case "invoices":
        return { title: "Invoices", category: "Audit & Ledger" };
      case "forecasting":
        return { title: "Sales Forecasting", category: "AI Insights" };
      case "segmentation":
        return { title: "Customer Segmentation", category: "AI Insights" };
      case "churn":
        return { title: "Churn Risk Intelligence", category: "AI Insights" };
      case "recommendations":
        return { title: "Product Recommendations", category: "AI Insights" };
      case "anomalies":
        return { title: "Anomaly Detection", category: "AI Insights" };
      case "reports":
        return { title: "Business Reports", category: "Export & Analytics" };
      case "data-upload":
        return { title: "Data Upload", category: "Data Sources" };
      case "settings":
        return { title: "System Settings", category: "Configuration" };
      default:
        return { title: "Dashboard", category: "Overview" };
    }
  };

  const meta = getPageMeta(activePage);

  return (
    <header className="app-header">
      <div className="header-title-area">
        <span className="header-category">{meta.category}</span>
        <h1 className="header-page-title">{meta.title}</h1>
      </div>

      <div className="header-right">
        {activeDatasetId && (
          <div className="header-dataset-badge" title={activeDatasetFilename || "Uploaded dataset active"}>
            <span />
            <span>Uploaded Data Active</span>
          </div>
        )}
        {canViewForecast && (
          <button
            className="btn-header-action"
            onClick={handleDownloadReport}
            disabled={isDownloadingReport}
          >
            <IconReports size={16} />
            <span>
              {isDownloadingReport ? "Generating..." : "Download Report"}
            </span>
          </button>
        )}

        <div className="user-profile-card">
          <div className="user-avatar">
            <IconUser size={18} color="#0f172a" />
          </div>
          <div className="user-info-text">
            <span className="user-name">{currentUsername || "User"}</span>
            <span className="user-role-badge">{userRole || "Member"}</span>
          </div>
        </div>

        <button className="btn-logout" onClick={handleLogout} title="Logout">
          <IconLogout size={18} />
        </button>
      </div>
    </header>
  );
}
