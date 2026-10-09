import React from "react";
import FilterBar from "../components/FilterBar";
import {
  IconAI,
  IconCustomers,
  IconForecasting,
  IconReports,
} from "../components/Icons";
import "./ReportsPage.css";

const reportSections = [
  {
    title: "Customer Segments",
    description:
      "Cohort profiles with purchase value, frequency and activity recency.",
    Icon: IconCustomers,
    color: "purple",
  },
  {
    title: "Sales Forecast",
    description: "Projected revenue for the selected forecast horizon.",
    Icon: IconForecasting,
    color: "blue",
  },
  {
    title: "Executive Summary",
    description: "Applied filters, forecast context, projected growth and key KPIs.",
    Icon: IconAI,
    color: "green",
  },
];

export default function ReportsPage({
  filters,
  setFilters,
  filterOptions,
  resetFilters,
  handleDownloadReport,
  isDownloadingReport,
  forecastHorizon,
  setForecastHorizon,
  canViewForecast,
}) {
  return (
    <div className="page-container reports-page">
      <FilterBar
        filters={filters}
        setFilters={setFilters}
        filterOptions={filterOptions}
        resetFilters={resetFilters}
      />

      <section className="reports-page-heading">
        <div className="reports-title-icon">
          <IconReports size={21} color="#6558d3" />
        </div>
        <div>
          <h2>Business Reports</h2>
          <p>
            Review key business insights and download the complete MarketMind
            report.
          </p>
        </div>
      </section>

      <section className="reports-overview-card">
        <div className="reports-overview-heading">
          <div className="reports-overview-icon">
            <IconReports size={20} color="#6558d3" />
          </div>
          <div>
            <span className="reports-eyebrow">MarketMind export</span>
            <h3>Your business report</h3>
          </div>
        </div>
        <p className="reports-overview-description">
          One Excel workbook bringing together customer segments, a sales
          forecast and an executive summary, based on the current filters.
        </p>
        <div className="reports-section-grid">
          {reportSections.map(({ title, description, Icon, color }) => (
            <article className="reports-section-card" key={title}>
              <span className={`reports-section-icon reports-icon-${color}`}>
                <Icon size={18} />
              </span>
              <div>
                <h4>{title}</h4>
                <p>{description}</p>
              </div>
            </article>
          ))}
        </div>
      </section>

      <section className="reports-download-card">
        <div className="reports-download-copy">
          <span className="reports-eyebrow">Ready when you are</span>
          <h3>Download Business Report</h3>
          <p>
            Export the existing report as an Excel workbook (.xlsx).
          </p>
        </div>
        <div className="reports-download-actions">
          <div className="reports-horizon-control">
            <label htmlFor="reports-horizon">Forecast horizon</label>
            <div className="reports-horizon-options" id="reports-horizon">
              {[30, 60, 90].map((horizon) => (
                <button
                  key={horizon}
                  type="button"
                  className={`reports-horizon-button ${
                    forecastHorizon === horizon ? "active" : ""
                  }`}
                  aria-pressed={forecastHorizon === horizon}
                  onClick={() => setForecastHorizon(horizon)}
                >
                  {horizon} days
                </button>
              ))}
            </div>
          </div>

          {canViewForecast ? (
            <button
              className="reports-download-button"
              type="button"
              onClick={handleDownloadReport}
              disabled={isDownloadingReport}
            >
              <IconReports size={17} color="currentColor" />
              {isDownloadingReport
                ? "Generating report..."
                : "Download Business Report"}
            </button>
          ) : (
            <p className="reports-access-note" role="status">
              Report downloads are restricted for your role. Contact your Store
              Manager or Administrator for access.
            </p>
          )}
        </div>
      </section>
    </div>
  );
}
