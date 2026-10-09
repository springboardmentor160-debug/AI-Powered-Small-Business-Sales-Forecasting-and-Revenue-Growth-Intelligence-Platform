import FilterBar from "../components/FilterBar";
import { IconSales, IconAI } from "../components/Icons";
import "./SalesPage.css";

export default function SalesPage({
  filters,
  setFilters,
  filterOptions,
  resetFilters,
  salesTrends,
  renderTrendChart,
  trendGranularity,
  setTrendGranularity,
  brandChannelData,
  citySales,
  categorySales,
  canViewMargin,
}) {
  // Metric Calculations
  const calculatedRevenueFromTrends = (salesTrends || []).reduce(
    (acc, item) => acc + Number(item.revenue || item.total_revenue || 0),
    0
  );

  const calculatedRevenueFromCategories = Object.values(categorySales || {}).reduce(
    (acc, val) => acc + Number(val || 0),
    0
  );

  const totalRevenue =
    calculatedRevenueFromTrends > 0
      ? calculatedRevenueFromTrends
      : calculatedRevenueFromCategories;

  const totalUnits = (brandChannelData?.by_brand || []).reduce(
    (acc, b) => acc + Number(b.units || 0),
    0
  );

  const totalMargin = (salesTrends || []).reduce(
    (acc, item) => acc + Number(item.margin || 0),
    0
  );

  const asp =
    totalUnits > 0 && totalRevenue > 0
      ? Math.round(totalRevenue / totalUnits)
      : 0;

  // Key Breakdown Leaders
  const topCityEntry = Object.entries(citySales || {}).reduce(
    (max, item) => (item[1] > max[1] ? item : max),
    ["—", 0]
  );

  const topCategoryEntry = Object.entries(categorySales || {}).reduce(
    (max, item) => (item[1] > max[1] ? item : max),
    ["—", 0]
  );

  const topBrandItem = (brandChannelData?.by_brand || [])[0] || null;
  const maxBrandRevenue = Math.max(
    ...(brandChannelData?.by_brand || []).map((brand) => Number(brand.revenue) || 0),
    1
  );
  const maxChannelRevenue = Math.max(
    ...(brandChannelData?.by_channel || []).map((channel) => Number(channel.revenue) || 0),
    1
  );
  const maxCategoryRevenue = Math.max(
    ...Object.values(categorySales || {}).map((value) => Number(value) || 0),
    1
  );
  const maxCityRevenue = Math.max(
    ...Object.values(citySales || {}).map((value) => Number(value) || 0),
    1
  );

  return (
    <div className="page-container sales-page-wrap">
      {/* GLOBAL DYNAMIC FILTER BAR */}
      <FilterBar
        filters={filters}
        setFilters={setFilters}
        filterOptions={filterOptions}
        resetFilters={resetFilters}
      />

      {/* 1. PAGE HEADER */}
      <div className="sales-header-block">
        <h1 className="sales-main-title">
          <IconSales size={24} color="#3b82f6" /> Sales Analytics
        </h1>
        <p className="sales-main-subtitle">
          Understand sales performance, revenue trends and product contribution
        </p>
      </div>

      {/* 2. SUMMARY KPI ROW */}
      <div className="sales-kpi-grid">
        <div className="sales-kpi-card card-sales-rev">
          <div className="sales-kpi-top">
            <span className="sales-kpi-label">Total Revenue</span>
            <span className="badge-blue-soft">Gross</span>
          </div>
          <div className="sales-kpi-value text-primary">
            ₹{totalRevenue.toLocaleString()}
          </div>
          <span className="sales-kpi-subtext">Total filtered earned revenue</span>
        </div>

        <div className="sales-kpi-card card-sales-vol">
          <div className="sales-kpi-top">
            <span className="sales-kpi-label">Sales Volume</span>
            <span className="badge-purple-soft">Units</span>
          </div>
          <div className="sales-kpi-value" style={{ color: "#8b5cf6" }}>
            {totalUnits.toLocaleString()} units
          </div>
          <span className="sales-kpi-subtext">Total units sold across brands</span>
        </div>

        {canViewMargin ? (
          <div className="sales-kpi-card card-sales-margin">
            <div className="sales-kpi-top">
              <span className="sales-kpi-label">Total Margin</span>
              <span className="badge-green-soft">Profit</span>
            </div>
            <div className="sales-kpi-value text-emerald">
              ₹{totalMargin.toLocaleString()}
            </div>
            <span className="sales-kpi-subtext">Filtered net profit margin</span>
          </div>
        ) : (
          <div className="sales-kpi-card card-sales-margin">
            <div className="sales-kpi-top">
              <span className="sales-kpi-label">Total Margin</span>
              <span className="badge-green-soft">Restricted</span>
            </div>
            <div className="sales-kpi-value text-muted">—</div>
            <span className="sales-kpi-subtext">Access restricted</span>
          </div>
        )}

        <div className="sales-kpi-card card-sales-asp">
          <div className="sales-kpi-top">
            <span className="sales-kpi-label">Avg Selling Price</span>
            <span className="badge-amber-soft">ASP</span>
          </div>
          <div className="sales-kpi-value text-amber">
            ₹{asp.toLocaleString()}
          </div>
          <span className="sales-kpi-subtext">Average revenue per unit</span>
        </div>
      </div>

      {/* 3. MAIN SALES CHART */}
      <div className="sales-card">
        <div className="sales-section-header">
          <div>
            <h3 className="sales-card-title">
              <IconSales size={18} color="#3b82f6" /> Sales & Margin Trend Performance
            </h3>
            <p className="sales-card-sub">
              Time-series sales {canViewMargin ? "and margin " : ""}trajectory over time based on active filters
            </p>
          </div>
          <div className="toggle-group-compact">
            <button
              className={`toggle-btn-sm ${trendGranularity === "monthly" ? "active" : ""}`}
              onClick={() => setTrendGranularity("monthly")}
            >
              Monthly
            </button>
            <button
              className={`toggle-btn-sm ${trendGranularity === "quarterly" ? "active" : ""}`}
              onClick={() => setTrendGranularity("quarterly")}
            >
              Quarterly
            </button>
          </div>
        </div>
        {renderTrendChart()}
      </div>

      {/* 4. BUSINESS INSIGHT CARD */}
      <div className="sales-insight-card">
        <div className="sales-insight-icon">
          <IconAI size={22} color="#2563eb" />
        </div>
        <div className="sales-insight-body" style={{ width: "100%" }}>
          <span className="sales-insight-label">Executive Performance Summary</span>
          <div className="sales-insight-grid">
            <div className="sales-insight-item">
              <span className="sales-insight-item-title">Top Category</span>
              <span className="sales-insight-item-val">{topCategoryEntry[0]}</span>
              <span className="sales-insight-item-sub">
                Leading product category with <strong>₹{Number(topCategoryEntry[1]).toLocaleString()}</strong> in filtered revenue.
              </span>
            </div>

            <div className="sales-insight-item">
              <span className="sales-insight-item-title">Top Brand</span>
              <span className="sales-insight-item-val">{topBrandItem?.brand || "—"}</span>
              <span className="sales-insight-item-sub">
                Highest brand contribution generating <strong>₹{Number(topBrandItem?.revenue || 0).toLocaleString()}</strong> across <strong>{(topBrandItem?.units || 0).toLocaleString()}</strong> units.
              </span>
            </div>

            <div className="sales-insight-item">
              <span className="sales-insight-item-title">Strongest Sales Region</span>
              <span className="sales-insight-item-val">{topCityEntry[0]}</span>
              <span className="sales-insight-item-sub">
                Leading geographic region contributing <strong>₹{Number(topCityEntry[1]).toLocaleString()}</strong> in total revenue.
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* 5. BRAND & FULFILLMENT BREAKDOWN */}
      <div className="sales-grid-2col">
        <div className="sales-card">
          <div className="sales-section-header">
            <div>
              <h3 className="sales-card-title">🏷️ Top Brand Revenue</h3>
              <p className="sales-card-sub">Revenue breakdown across FMCG brands</p>
            </div>
          </div>

          <div className="brand-bar-list">
            {(brandChannelData?.by_brand || []).map((b) => {
              const widthPct = Math.round((Number(b.revenue || 0) / maxBrandRevenue) * 100);
              return (
                <div className="brand-bar-row" key={b.brand}>
                  <div className="brand-row-info">
                    <span className="brand-name-text">{b.brand}</span>
                    <span className="brand-val-text">
                      <strong>₹{Number(b.revenue).toLocaleString()}</strong>
                      <span>{Number(b.units).toLocaleString()} units</span>
                    </span>
                  </div>
                  <div
                    className="brand-bar-track"
                    role="img"
                    aria-label={`${b.brand}: ${widthPct}% of the highest brand revenue`}
                  >
                    <div className="brand-bar-fill" style={{ width: `${widthPct}%` }} />
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        <div className="sales-card">
          <div className="sales-section-header">
            <div>
              <h3 className="sales-card-title">📡 Fulfillment Channels</h3>
              <p className="sales-card-sub">Revenue and volume distribution by sales channel</p>
            </div>
          </div>

          <div className="channel-card-list">
            {(brandChannelData?.by_channel || []).map((ch) => {
              const widthPct = Math.round((Number(ch.revenue || 0) / maxChannelRevenue) * 100);
              return (
                <div className="channel-card-item" key={ch.channel}>
                  <div className="channel-card-details">
                    <div className="channel-card-heading">
                      <div>
                        <div className="channel-name">{ch.channel}</div>
                        <div className="channel-sub">{Number(ch.units).toLocaleString()} units sold</div>
                      </div>
                      <div className="channel-rev font-bold text-success">
                        ₹{Number(ch.revenue).toLocaleString()}
                      </div>
                    </div>
                    <div
                      className="channel-progress-track"
                      role="img"
                      aria-label={`${ch.channel}: ${widthPct}% of the highest channel revenue`}
                    >
                      <span style={{ width: `${widthPct}%` }} />
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* 6. CATEGORY & CITY BREAKDOWN */}
      <div className="sales-grid-2col">
        <div className="sales-card">
          <div className="sales-section-header">
            <div>
              <h3 className="sales-card-title">📁 Revenue by Category</h3>
              <p className="sales-card-sub">Product category revenue totals</p>
            </div>
          </div>

          <div className="table-responsive">
            <table className="sales-mini-table">
              <thead>
                <tr>
                  <th>Category</th>
                  <th>Revenue Total</th>
                </tr>
              </thead>
              <tbody>
                {Object.entries(categorySales || {}).map(([cat, val]) => {
                  const widthPct = Math.round((Number(val || 0) / maxCategoryRevenue) * 100);
                  return (
                    <tr key={cat}>
                      <td>
                        <strong>{cat}</strong>
                        <div className="sales-table-progress" aria-hidden="true">
                          <span style={{ width: `${widthPct}%` }} />
                        </div>
                      </td>
                      <td className="sales-table-value">₹{Number(val).toLocaleString()}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>

        <div className="sales-card">
          <div className="sales-section-header">
            <div>
              <h3 className="sales-card-title">🏙️ Revenue by City</h3>
              <p className="sales-card-sub">Geographic sales performance</p>
            </div>
          </div>

          <div className="table-responsive">
            <table className="sales-mini-table">
              <thead>
                <tr>
                  <th>City</th>
                  <th>Revenue Total</th>
                </tr>
              </thead>
              <tbody>
                {Object.entries(citySales || {}).map(([city, val]) => {
                  const widthPct = Math.round((Number(val || 0) / maxCityRevenue) * 100);
                  return (
                    <tr key={city}>
                      <td>
                        <strong>{city}</strong>
                        <div className="sales-table-progress" aria-hidden="true">
                          <span style={{ width: `${widthPct}%` }} />
                        </div>
                      </td>
                      <td className="sales-table-value">₹{Number(val).toLocaleString()}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
