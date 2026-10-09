import FilterBar from "../components/FilterBar";
import {
  IconAI,
  IconAnomaly,
  IconForecasting,
  IconInventory,
  IconSegmentation,
} from "../components/Icons";
import "./InventoryPage.css";

export default function InventoryPage({
  filters,
  setFilters,
  filterOptions,
  resetFilters,
  inventoryIntel,
  canViewLowStock,
}) {
  if (!canViewLowStock) {
    return (
      <div className="page-container inv-page-wrap">
        <FilterBar
          filters={filters}
          setFilters={setFilters}
          filterOptions={filterOptions}
          resetFilters={resetFilters}
        />
        <div className="inv-card" style={{ marginTop: "12px" }}>
          <div className="inv-section-header">
            <div>
              <h3 className="inv-card-title text-danger">🔒 Access Restricted</h3>
              <p className="inv-card-sub">
                Inventory Intelligence is accessible to Store Managers, Business Owners, and Administrators only.
              </p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  const criticalItems = inventoryIntel?.critical_items || [];
  const totalLowStock = inventoryIntel?.total_low_stock_count || 0;
  const byCategory = inventoryIntel?.by_category || {};

  // KPI Calculations
  const criticalDeficitCount = criticalItems.filter((item) => item.deficit > 20).length;

  const topCategoryPair = Object.entries(byCategory).reduce(
    (max, item) => (item[1] > max[1] ? item : max),
    ["—", 0]
  );

  const avgLeadTime =
    criticalItems.length > 0
      ? Math.round(
          criticalItems.reduce((acc, item) => acc + Number(item.lead_time_days || 0), 0) /
            criticalItems.length
        )
      : 0;

  return (
    <div className="page-container inv-page-wrap">
      {/* GLOBAL DYNAMIC FILTER BAR */}
      <FilterBar
        filters={filters}
        setFilters={setFilters}
        filterOptions={filterOptions}
        resetFilters={resetFilters}
      />

      {/* 1. PAGE HEADER */}
      <div className="inv-header-block">
        <h1 className="inv-main-title">
          <IconInventory size={24} color="#f59e0b" /> Inventory Intelligence
        </h1>
        <p className="inv-main-subtitle">
          Monitor stock health and identify items that need attention.
        </p>
      </div>

      {/* 2. SUMMARY KPI ROW */}
      <div className="inv-kpi-grid">
        <div className="inv-kpi-card card-inv-total">
          <div className="inv-kpi-top">
            <span className="inv-kpi-label">Total Low Stock Items</span>
            <span className="inv-kpi-icon inv-kpi-icon-total"><IconInventory size={17} /></span>
          </div>
          <div className="inv-kpi-value text-danger">
            {totalLowStock.toLocaleString()}
          </div>
          <span className="inv-kpi-foot">
            <span className="badge-danger-soft">Reorder Required</span>
            <span className="inv-kpi-subtext">Items below safety threshold</span>
          </span>
        </div>

        <div className="inv-kpi-card card-inv-critical">
          <div className="inv-kpi-top">
            <span className="inv-kpi-label">Critical Deficit Items</span>
            <span className="inv-kpi-icon inv-kpi-icon-critical"><IconAnomaly size={17} /></span>
          </div>
          <div className="inv-kpi-value text-amber">
            {criticalDeficitCount.toLocaleString()}
          </div>
          <span className="inv-kpi-foot">
            <span className="badge-amber-soft">High Priority</span>
            <span className="inv-kpi-subtext">Deficit &gt; 20 units requiring urgent order</span>
          </span>
        </div>

        <div className="inv-kpi-card card-inv-category">
          <div className="inv-kpi-top">
            <span className="inv-kpi-label">Top Category Deficit</span>
            <span className="inv-kpi-icon inv-kpi-icon-category"><IconSegmentation size={17} /></span>
          </div>
          <div className="inv-kpi-value text-primary">
            {topCategoryPair[0]}
          </div>
          <span className="inv-kpi-foot">
            <span className="badge-blue-soft">Category Focus</span>
            <span className="inv-kpi-subtext">
              {topCategoryPair[1] > 0 ? `${topCategoryPair[1]} low stock items` : "No category alerts"}
            </span>
          </span>
        </div>

        <div className="inv-kpi-card card-inv-lead">
          <div className="inv-kpi-top">
            <span className="inv-kpi-label">Avg Lead Time</span>
            <span className="inv-kpi-icon inv-kpi-icon-lead"><IconForecasting size={17} /></span>
          </div>
          <div className="inv-kpi-value text-emerald">
            {avgLeadTime > 0 ? `${avgLeadTime} days` : "—"}
          </div>
          <span className="inv-kpi-foot">
            <span className="badge-green-soft">Fulfillment</span>
            <span className="inv-kpi-subtext">Average vendor delivery turnaround</span>
          </span>
        </div>
      </div>

      {/* 3. MAIN INVENTORY OVERVIEW / CRITICAL REORDER TABLE */}
      <div className="inv-card">
        <div className="inv-section-header">
          <div>
            <h3 className="inv-card-title">🚨 Low Stock & Priority Reorder Items</h3>
            <p className="inv-card-sub">
              Stock items sorted by deficit level and vendor lead time — immediate action required
            </p>
          </div>
          <span className="badge-danger-soft inv-urgent-count">
            {criticalItems.length} Urgent Items
          </span>
        </div>

        <div className="table-responsive inv-table-responsive">
          <table className="inv-action-table">
            <thead>
              <tr>
                <th>Invoice / Ref</th>
                <th>Store City</th>
                <th>Product Brand & Category</th>
                <th>Stock On Hand</th>
                <th>Reorder Level</th>
                <th>Deficit</th>
                <th>Lead Time</th>
                <th>Stock Status</th>
              </tr>
            </thead>
            <tbody>
              {criticalItems.map((item, idx) => {
                const isCritical = item.deficit > 20;
                return (
                  <tr key={idx}>
                    <td>
                      <span className="inv-id-pill">#{item.invoice_id}</span>
                    </td>
                    <td>{item.city}</td>
                    <td>
                      <strong>{item.brand}</strong>
                      <div className="mini-subtext">{item.category}</div>
                    </td>
                    <td>
                      <strong style={{ color: "#0f172a" }}>{item.stock_on_hand}</strong>
                    </td>
                    <td>{item.reorder_level}</td>
                    <td className="inv-deficit-cell">-{item.deficit}</td>
                    <td>{item.lead_time_days} days</td>
                    <td>
                      {isCritical ? (
                        <span className="badge-danger-soft inv-status-badge">CRITICAL</span>
                      ) : (
                        <span className="badge-amber-soft inv-status-badge">REORDER</span>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* 4. SUPPORTING SECTION: CATEGORY DEFICIT CONCENTRATION & INSIGHTS */}
      <div className="inv-grid-2col">
        {/* Category Breakdown Bar List */}
        <div className="inv-card">
          <div className="inv-section-header">
            <div>
              <h3 className="inv-card-title">📁 Reorder Deficit by Category</h3>
              <p className="inv-card-sub">Concentration of low stock items by product category</p>
            </div>
          </div>

          <div className="brand-bar-list inv-category-list">
            {Object.entries(byCategory).map(([cat, count]) => {
              const maxCat = Object.values(byCategory)[0] || 1;
              const widthPct = Math.round((count / maxCat) * 100);
              return (
                <div className="brand-bar-row inv-category-row" key={cat}>
                  <div className="brand-row-info">
                    <span className="brand-name-text">{cat}</span>
                    <span className="inv-category-count">
                      {count}
                    </span>
                  </div>
                  <div className="brand-bar-track inv-category-track">
                    <div
                      className="brand-bar-fill"
                      style={{
                        width: `${widthPct}%`,
                        backgroundColor: count > 10 ? "#ef4444" : "#f59e0b",
                      }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Operational Guidelines & Insights Card */}
        <div className="inv-card inv-guidance-card">
          <div className="inv-section-header">
            <div>
              <h3 className="inv-card-title">
                <IconAI size={18} color="#4776e6" /> Operational Reorder Focus
              </h3>
              <p className="inv-card-sub">Procurement recommendations based on current stock data</p>
            </div>
          </div>

          <div className="inv-guidance-list">
            <div className="inv-guidance-item inv-guidance-priority">
              <div className="inv-guidance-heading">
                <span className="inv-guidance-icon"><IconAnomaly size={16} /></span>
                <span className="inv-kpi-label">Reorder Priority</span>
                <strong>{criticalDeficitCount}</strong>
              </div>
              <p>
                <strong>{criticalDeficitCount} items</strong> exhibit severe deficits exceeding 20 units. Initiate procurement orders with primary vendors immediately.
              </p>
            </div>

            <div className="inv-guidance-item inv-guidance-vendor">
              <div className="inv-guidance-heading">
                <span className="inv-guidance-icon"><IconForecasting size={16} /></span>
                <span className="inv-kpi-label">Vendor Turnaround</span>
                <strong>{avgLeadTime} days</strong>
              </div>
              <p>
                Average vendor delivery lead time is <strong>{avgLeadTime} days</strong>. Plan purchase orders buffer to prevent out-of-stock events.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
