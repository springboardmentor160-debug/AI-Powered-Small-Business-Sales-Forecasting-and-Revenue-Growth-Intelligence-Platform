import { useState } from "react";
import FilterBar from "../components/FilterBar";
import {
  IconAnomaly,
  IconChurn,
  IconInventory,
  IconInvoices,
} from "../components/Icons";
import "./InvoicesPage.css";

const getStatusClass = (status) => {
  switch (String(status || "").toUpperCase()) {
    case "CRITICAL":
      return "badge-critical";
    case "HIGH":
    case "REORDER NEEDED":
      return "badge-warning";
    case "MEDIUM":
      return "badge-medium";
    case "LOW":
    case "NORMAL":
      return "badge-low";
    default:
      return "badge-neutral";
  }
};

function InvoiceDetails({ detail }) {
  const stockDetail = detail.match(/^Stock:\s*(.*?)\s*\|\s*Deficit:\s*(-?\s*.+)$/);
  if (!stockDetail) {
    return <span className="invoices-detail-text">{detail}</span>;
  }

  return (
    <span className="invoices-detail-parts">
      <span><small>Stock</small><strong>{stockDetail[1]}</strong></span>
      <span>
        <small>Deficit</small>
        <strong className={stockDetail[2].trim().startsWith("-") ? "invoices-negative" : ""}>
          {stockDetail[2].trim()}
        </strong>
      </span>
    </span>
  );
}

export default function InvoicesPage({
  filters,
  setFilters,
  filterOptions,
  resetFilters,
  inventoryIntel,
  anomalyData,
  churnData,
}) {
  const [searchTerm, setSearchTerm] = useState("");

  const criticalInvoices = (inventoryIntel.critical_items || []).map((item) => ({
    invoice_id: item.invoice_id,
    city: item.city,
    category: item.category,
    brand: item.brand,
    type: "Inventory Alert",
    status: item.deficit > 20 ? "CRITICAL" : "REORDER NEEDED",
    statusClass: item.deficit > 20 ? "badge-critical" : "badge-warning",
    detail: `Stock: ${item.stock_on_hand} | Deficit: -${item.deficit}`,
  }));

  const anomalyInvoices = (anomalyData?.anomalies || []).map((anom) => ({
    invoice_id: anom.invoice_id,
    city: anom.city,
    category: anom.category,
    brand: anom.brand,
    type: `Anomaly: ${anom.anomaly_type}`,
    status: anom.severity,
    statusClass: getStatusClass(anom.severity),
    detail: anom.reason,
  }));

  const churnInvoices = (churnData?.sample_high_risk_invoices || []).map((inv) => ({
    invoice_id: inv.invoice_id,
    city: inv.city,
    category: inv.category,
    brand: inv.brand,
    type: "Churn Risk",
    status: inv.risk_category.toUpperCase(),
    statusClass: getStatusClass(inv.risk_category),
    detail: `Inactivity: ${inv.inactivity_days} days | Churn Prob: ${inv.churn_risk_pct}`,
  }));

  const allInvoicesMap = new Map();
  [...criticalInvoices, ...anomalyInvoices, ...churnInvoices].forEach((item) => {
    if (!allInvoicesMap.has(item.invoice_id)) {
      allInvoicesMap.set(item.invoice_id, item);
    }
  });

  const invoiceList = Array.from(allInvoicesMap.values());

  const filteredInvoices = invoiceList.filter((inv) => {
    const term = searchTerm.toLowerCase();
    return (
      inv.invoice_id.toString().toLowerCase().includes(term) ||
      inv.city.toLowerCase().includes(term) ||
      inv.brand.toLowerCase().includes(term) ||
      inv.category.toLowerCase().includes(term) ||
      inv.type.toLowerCase().includes(term)
    );
  });

  return (
    <div className="page-container invoices-page">
      <section className="invoices-page-heading">
        <div className="invoices-title-icon">
          <IconInvoices size={21} color="#6558d3" />
        </div>
        <div>
          <h2>Invoices</h2>
          <p>Review sales transactions and payment details in one place.</p>
        </div>
      </section>

      <section className="invoices-kpi-grid" aria-label="Invoice record summary">
        <article className="invoices-kpi-card invoices-kpi-purple">
          <span className="invoices-kpi-icon invoices-kpi-icon-flagged"><IconInvoices size={17} /></span>
          <span className="invoices-kpi-label">Flagged Invoice Records</span>
          <strong>{invoiceList.length.toLocaleString()}</strong>
          <small>Records surfaced for review</small>
        </article>
        <article className="invoices-kpi-card invoices-kpi-amber">
          <span className="invoices-kpi-icon invoices-kpi-icon-inventory"><IconInventory size={17} /></span>
          <span className="invoices-kpi-label">Inventory Alerts</span>
          <strong>{criticalInvoices.length.toLocaleString()}</strong>
          <small>Records with a stock or reorder signal</small>
        </article>
        <article className="invoices-kpi-card invoices-kpi-blue">
          <span className="invoices-kpi-icon invoices-kpi-icon-anomaly"><IconAnomaly size={17} /></span>
          <span className="invoices-kpi-label">Anomaly Flags</span>
          <strong>{anomalyInvoices.length.toLocaleString()}</strong>
          <small>Records identified by anomaly analysis</small>
        </article>
        <article className="invoices-kpi-card invoices-kpi-rose">
          <span className="invoices-kpi-icon invoices-kpi-icon-churn"><IconChurn size={17} /></span>
          <span className="invoices-kpi-label">Churn-risk Records</span>
          <strong>{churnInvoices.length.toLocaleString()}</strong>
          <small>High-risk sample records available</small>
        </article>
      </section>

      <section className="invoices-controls-card" aria-label="Invoice filters and search">
        <FilterBar
          filters={filters}
          setFilters={setFilters}
          filterOptions={filterOptions}
          resetFilters={resetFilters}
        />
        <div className="invoices-search-wrap">
          <label htmlFor="invoice-search">Search Flagged Records</label>
          <input
            id="invoice-search"
            type="search"
            className="invoices-search-input"
            placeholder="Invoice ID, city, brand, category..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
      </section>

      <section className="invoices-table-card">
        <div className="invoices-table-heading">
          <div>
            <span className="invoices-eyebrow">Transaction Review</span>
            <h3>Flagged Invoice Records</h3>
          </div>
          <span className="invoices-result-count">
            {filteredInvoices.length.toLocaleString()} records
          </span>
        </div>

        <div className="invoices-table-scroll">
          <table className="invoices-table">
            <thead>
              <tr>
                <th>Invoice ID</th>
                <th>City</th>
                <th>Brand / Category</th>
                <th>Signal</th>
                <th>Indicator</th>
                <th>Details</th>
              </tr>
            </thead>
            <tbody>
              {filteredInvoices.length > 0 ? (
                filteredInvoices.map((inv) => (
                  <tr key={inv.invoice_id}>
                    <td>
                      <span className="invoices-id">#{inv.invoice_id}</span>
                    </td>
                    <td>{inv.city}</td>
                    <td>
                      <strong className="invoices-brand">{inv.brand}</strong>
                      <span className="invoices-category">{inv.category}</span>
                    </td>
                    <td>
                      <span className="invoices-signal">{inv.type}</span>
                    </td>
                    <td>
                      <span className={`invoices-status ${inv.statusClass}`}>
                        {inv.status}
                      </span>
                    </td>
                    <td className="invoices-detail"><InvoiceDetails detail={inv.detail} /></td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="6" className="invoices-empty">
                    No matching invoice records found.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
        <p className="invoices-data-note">
          This view lists records surfaced by inventory, anomaly, and churn
          analysis. The available feed does not include complete transaction
          totals, dates, units, payment modes, or channels.
        </p>
      </section>
    </div>
  );
}
